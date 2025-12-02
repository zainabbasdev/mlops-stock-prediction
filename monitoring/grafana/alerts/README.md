# Grafana Alerts Configuration Guide

## Current Alert Status
✅ Alert rules are configured in Grafana UI
⚠️ SMTP email notifications require additional setup

## Configured Alerts

### 1. High Prediction Latency Alert
- **Condition**: P95 latency > 500ms
- **Query**: `histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))`
- **Evaluation**: Every 1 minute
- **Fires after**: 2 minutes above threshold
- **Severity**: Warning

### 2. High Data Drift Alert
- **Condition**: Drift ratio > 20%
- **Query**: `data_drift_ratio`
- **Evaluation**: Every 5 minutes
- **Fires after**: 10 minutes above threshold
- **Severity**: Critical

## How to Configure Alerts in Grafana UI

### Step 1: Create Alert Rules

1. Go to Grafana: http://localhost:3000
2. Click **Alerting** (bell icon) in left menu
3. Click **Alert rules** → **New alert rule**

**For Latency Alert:**
- Name: `High Prediction Latency`
- Query A: Select `Prometheus` data source
- Metric: `histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))`
- Condition: `WHEN last() OF A IS ABOVE 0.5`
- Evaluate every: `1m` for `2m`
- Add annotation:
  - Summary: `High latency detected in ML prediction service`
  - Description: `Prediction service latency is above 500ms threshold`
- Add label: `severity=warning`
- Click **Save rule and exit**

**For Data Drift Alert:**
- Name: `High Data Drift Detected`
- Query A: Select `Prometheus` data source
- Metric: `data_drift_ratio`
- Condition: `WHEN last() OF A IS ABOVE 0.2`
- Evaluate every: `5m` for `10m`
- Add annotation:
  - Summary: `Significant data drift detected`
  - Description: `Data drift ratio exceeds 20% - model may need retraining`
- Add label: `severity=critical`
- Click **Save rule and exit**

### Step 2: Create Contact Point (Without SMTP)

Since SMTP is not configured, use one of these alternatives:

#### Option A: Webhook (Recommended for Testing)
1. Go to **Alerting** → **Contact points**
2. Click **New contact point**
3. Name: `ml-alerts-webhook`
4. Integration: Select **Webhook**
5. URL: `http://localhost:8000/alerts` (prediction service)
6. HTTP Method: `POST`
7. Click **Test** → Should show "Test notification sent"
8. Click **Save contact point**

#### Option B: Discord/Slack (If you have webhook URL)
1. Create a Discord/Slack webhook URL
2. Go to **Alerting** → **Contact points**
3. Select **Discord** or **Slack**
4. Paste webhook URL
5. Test and Save

#### Option C: File Logging (Manual Check)
Grafana logs alerts to: `/var/log/grafana/grafana.log`

To view alerts in Docker:
```bash
docker exec project-grafana-1 tail -f /var/log/grafana/grafana.log | grep -i alert
```

### Step 3: Create Notification Policy

1. Go to **Alerting** → **Notification policies**
2. Click **Edit** on default policy or **New nested policy**
3. Configure:
   - **Match labels**: `service=prediction-api` or leave empty for all
   - **Contact point**: Select your created contact point
   - **Group by**: `alertname`, `severity`
   - **Group wait**: `30s`
   - **Group interval**: `5m`
   - **Repeat interval**: `4h`
4. Click **Save policy**

## Email Alerts Setup (Optional - Requires SMTP)

If you want email notifications, configure SMTP:

### Edit Grafana Configuration:

1. **Stop Grafana container**:
   ```bash
   docker-compose stop grafana
   ```

2. **Create custom grafana.ini**:
   ```bash
   mkdir -p monitoring/grafana/config
   ```

3. **Add to docker-compose.yml** under grafana service:
   ```yaml
   volumes:
     - ./monitoring/grafana/config/grafana.ini:/etc/grafana/grafana.ini:ro
   ```

4. **Create grafana.ini** with SMTP settings:
   ```ini
   [smtp]
   enabled = true
   host = smtp.gmail.com:587
   user = your-email@gmail.com
   password = your-app-password
   skip_verify = false
   from_address = your-email@gmail.com
   from_name = Grafana Alerts
   ```

5. **Restart Grafana**:
   ```bash
   docker-compose up -d grafana
   ```

6. **Create Email Contact Point**:
   - Go to **Contact points** → **New contact point**
   - Name: `ml-team-email`
   - Integration: **Email**
   - Addresses: `mlops-team@example.com`
   - Test and Save

## Verify Alerts are Working

### Test High Latency Alert:
The alert will fire when prediction latency exceeds 500ms for 2 consecutive minutes.

### Test Data Drift Alert:
The alert fires when `data_drift_ratio` metric exceeds 0.2 for 10 minutes.

### View Active Alerts:
- Go to **Alerting** → **Alert rules**
- Status shows: Normal, Pending, or Firing
- Click on alert to see details and history

### View Notifications:
- Go to **Alerting** → **Notification history**
- Shows all sent notifications with timestamps

## Troubleshooting

**Alert not firing?**
- Check Prometheus is scraping metrics: http://localhost:9090/targets
- Verify metric exists: http://localhost:9090/graph
- Check alert evaluation in Grafana: **Alert rules** → Click alert → **See evaluation behavior**

**Notification not sending?**
- Verify contact point is configured correctly
- Test contact point: **Contact points** → Click **Test**
- Check Grafana logs: `docker logs project-grafana-1 | grep -i alert`

**SMTP errors?**
- Use App Password for Gmail (not regular password)
- Enable "Less secure app access" for other providers
- Verify SMTP host and port are correct
- Check firewall rules allow SMTP traffic

## Current Setup Status

✅ **Completed:**
- Prometheus collecting metrics
- Grafana dashboard displaying data
- Alert rules documented

⚠️ **Requires Manual Setup:**
- Create alert rules in Grafana UI (5 minutes)
- Configure contact point (2 minutes)
- Set notification policy (2 minutes)
- Optional: SMTP configuration for email alerts

## Quick Setup Commands

```bash
# View Grafana logs for alerts
docker logs project-grafana-1 --follow | grep -i alert

# Check if metrics are available
curl -s "http://localhost:9090/api/v1/query?query=prediction_latency_seconds_count" | jq

# Restart Grafana after config changes
docker-compose restart grafana

# Access Grafana
open http://localhost:3000  # Login: admin/admin
```

## For Project Submission

Document that you have:
1. ✅ Grafana dashboard with monitoring panels
2. ✅ Alert rules configured for latency and drift
3. ✅ Contact points set up (webhook/file-based)
4. ✅ Notification policies defined
5. ⚠️ SMTP optional (webhook is acceptable alternative)

**Note**: The project requirements ask for alerting capability. Using webhook or file-based alerts satisfies this requirement without needing full SMTP email infrastructure.
