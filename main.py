"""
FasalWatch — Main Multi-Agent Orchestrator (AWS-Powered)
Built with Strands Agents SDK, Open-Meteo, AWS DynamoDB, Amazon Translate, and Amazon SNS.

Pipeline:
  1. Profile Layer  → Fetch farmer profile from AWS DynamoDB ('FasalWatch_Farmers')
  2. Data Layer     → Fetch 7-day live weather forecast from Open-Meteo API
  3. Risk Layer     → Deterministic risk calculation + Strands Risk Agent explanation
  4. Advisor Layer  → Strands Advisor Agent (concrete, non-jargon mitigation steps)
  5. Localize Layer → AWS Amazon Translate (Grade 5 native language + SMS < 160 chars)
  6. Review Layer   → Strands Reviewer Agent (checks safety, contradictions, tone)
  7. Alert Layer    → AWS Amazon SNS (publishes alert & logs to topic)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.dynamo_tool import get_farmer_profile_db, init_dynamodb_table
from tools.weather_tool import get_weather_forecast
from tools.risk_calculator import calculate_risk
from tools.sns_tool import publish_sns_alert
from agents.risk_agent import run_risk_agent
from agents.advisor_agent import run_advisor_agent
from agents.localizer_agent import run_localizer_agent
from agents.reviewer_agent import run_reviewer_agent


def build_weather_summary(farmer: dict, raw: dict) -> str:
    s = raw["summary"]
    lines = [f"Location: {farmer['location']} (Lat {farmer['latitude']}, Lon {farmer['longitude']})"]
    lines.append(f"Crop: {farmer['crop'].title()} at {farmer['stage'].replace('_', ' ')} stage")
    lines.append("\n7-Day Daily Forecast:")
    for d in raw["forecast_days"]:
        lines.append(
            f"  {d['date']}: Max {d['max_temp_c']}°C | Min {d['min_temp_c']}°C | "
            f"Rain {d['precipitation_mm']}mm"
        )
    lines.append(f"\nWeek Summary:")
    lines.append(f"  Total rainfall   : {s['total_rainfall_7day_mm']} mm")
    lines.append(f"  Peak temperature : {s['max_temperature_7day_c']}°C")
    lines.append(f"  Days above 35°C  : {s['days_above_35c']}")
    lines.append(f"  Days above 38°C  : {s['days_above_38c']}")
    return "\n".join(lines)


def run_fasalwatch(farmer_id: str = "farmer_001") -> dict:
    print(f"\n{'='*65}")
    print(f"🌾 FASALWATCH — AWS MULTI-AGENT EARLY WARNING SYSTEM")
    print(f"{'='*65}")

    # 1. Farmer Profile via AWS DynamoDB
    print(f"📦 [Step 1/6] Fetching farmer profile from AWS DynamoDB...")
    p_res = get_farmer_profile_db(farmer_id)
    if p_res["status"] != "found":
        print(f"❌ Farmer profile '{farmer_id}' not found.")
        return {"error": "Profile not found"}
    farmer = p_res["farmer"]
    print(f"✅ Farmer Profile Loaded ({p_res.get('source', 'dynamodb')})")
    print(f"   Name: {farmer['name']} | Location: {farmer['location']}")
    print(f"   Crop: {farmer['crop'].title()} ({farmer['stage'].replace('_', ' ')}) | Lang: {farmer['language_name']}")

    # 2. Weather Forecast
    print(f"\n📡 [Step 2/6] Fetching live 7-day forecast from Open-Meteo...")
    raw_weather = get_weather_forecast(
        latitude=float(farmer["latitude"]),
        longitude=float(farmer["longitude"]),
        location_name=farmer["location"]
    )
    if raw_weather["status"] != "success":
        print(f"❌ Weather fetch failed: {raw_weather.get('error')}")
        return {"error": raw_weather.get("error")}

    weather_summary = build_weather_summary(farmer, raw_weather)
    print(f"✅ Weather forecast received for {farmer['location']}.")

    # 3. Risk Assessment (Deterministic + Strands Agent)
    print(f"\n⚠️  [Step 3/6] Risk Assessment (Python Calculator + Strands Risk Agent)...")
    calc = calculate_risk(
        crop=farmer["crop"],
        stage=farmer["stage"],
        forecast_days=raw_weather["forecast_days"],
        total_rain_mm=raw_weather["summary"]["total_rainfall_7day_mm"]
    )
    risk_level = calc["risk_level"]
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(risk_level, "⚪")
    print(f"  Calculated Risk: {risk_emoji} {risk_level} (Peak: {calc['peak_temp_c']}°C, Consec days: {calc['max_consecutive_heat_days']})")

    risk_output = run_risk_agent(
        crop=farmer["crop"],
        stage=farmer["stage"],
        forecast_summary=weather_summary,
        forced_risk_level=risk_level,
        calc_details=calc
    )
    print(f"✅ Strands Risk Agent completed explanation.")

    # 4. Advisor Agent
    print(f"\n💡 [Step 4/6] Strands Advisor Agent: Formulating practical actions...")
    actions = run_advisor_agent(
        crop=farmer["crop"],
        stage=farmer["stage"],
        risk_level=risk_level,
        risk_explanation=risk_output,
        forecast_summary=weather_summary
    )
    print(f"✅ Farm actions generated.")

    # 5. Localizer Agent via AWS Amazon Translate
    print(f"\n🌐 [Step 5/6] Localizer Agent: Translating via AWS Amazon Translate...")
    localized = run_localizer_agent(
        actions=actions,
        risk_level=risk_level,
        language_code=farmer["language"],
        farmer_name=farmer["name"],
        crop=farmer["crop"]
    )
    print(f"✅ Advisory localized into {farmer['language_name']} ({localized.get('sms_char_count')} chars).")

    # 6. Reviewer Agent
    print(f"\n🔍 [Step 6/6] Strands Reviewer Agent: Auditing advisory safety & clarity...")
    review = run_reviewer_agent(
        risk_level=risk_level,
        english_actions=actions,
        sms_version=localized["sms_version"],
        full_version=localized["full_version"],
        back_translation=localized["back_translation"]
    )
    rev_status = "APPROVED" if review["approved"] else "FLAGGED"
    print(f"✅ Audit Result: {rev_status}")

    # 7. Publish Alert via AWS SNS
    print(f"\n📲 Dispatching Alert via AWS Amazon SNS...")
    sns_res = publish_sns_alert(
        farmer_name=farmer["name"],
        farmer_phone=farmer["phone"],
        short_advisory=localized["sms_version"],
        full_advisory=localized["full_version"],
        risk_level=risk_level,
        language=farmer["language_name"]
    )

    print(f"{'='*65}")
    print(f"📋 FINAL ADVISORY READY")
    print(f"{'='*65}")
    print(f"Recipient: {farmer['name']} ({farmer['phone']}) - {farmer['location']}")
    print(f"Status   : {risk_emoji} {risk_level} Risk")
    print(f"SMS Msg  : {localized['sms_version']}")
    print(f"Topic ARN: {sns_res.get('topic_arn')}")
    print(f"Msg ID   : {sns_res.get('message_id')}")
    print(f"{'='*65}\n")

    return {
        "farmer": farmer,
        "risk_level": risk_level,
        "calc": calc,
        "risk_explanation": risk_output,
        "actions": actions,
        "localized": localized,
        "review": review,
        "sns": sns_res,
        "weather_summary": weather_summary
    }


if __name__ == "__main__":
    fid = sys.argv[1] if len(sys.argv) > 1 else "farmer_001"
    run_fasalwatch(fid)
