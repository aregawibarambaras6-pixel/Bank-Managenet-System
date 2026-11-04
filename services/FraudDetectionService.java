import java.util.*;
import java.time.Instant;

/**
 * Enterprise Banking Anti-Money Laundering (AML) & Fraud Detection Service
 * Written in Java 25
 */
public class FraudDetectionService {

    public static class RiskAssessment {
        public String referenceId;
        public String status; // APPROVED, FLAGGED, REJECTED
        public int riskScore; // 0 to 100
        public String riskLevel; // LOW, MEDIUM, HIGH, CRITICAL
        public List<String> rulesTriggered = new ArrayList<>();
        public String recommendation;
    }

    public static RiskAssessment analyzeTransaction(String referenceId, String transactionType, double amount, 
                                                    String accountType, String senderStatus, int dailyTxnCount) {
        RiskAssessment assessment = new RiskAssessment();
        assessment.referenceId = referenceId;
        int score = 0;

        // Rule 1: High Transaction Value AML Check ($10,000 threshold)
        if (amount >= 10000.0) {
            score += 45;
            assessment.rulesTriggered.add("HIGH_VALUE_AML_THRESHOLD_EXCEEDED (Amount >= $10,000.00)");
        } else if (amount >= 5000.0) {
            score += 20;
            assessment.rulesTriggered.add("ELEVATED_VALUE_TRANSFER (Amount >= $5,000.00)");
        }

        // Rule 2: High Velocity Burst (Too many transactions in a short period)
        if (dailyTxnCount >= 10) {
            score += 35;
            assessment.rulesTriggered.add("VELOCITY_SPIKE_DETECTED (Daily transactions >= 10)");
        } else if (dailyTxnCount >= 5) {
            score += 15;
            assessment.rulesTriggered.add("MODERATE_VELOCITY (Daily transactions >= 5)");
        }

        // Rule 3: Account Status anomaly
        if (!"active".equalsIgnoreCase(senderStatus)) {
            score += 50;
            assessment.rulesTriggered.add("DORMANT_OR_RESTRICTED_ACCOUNT_ACTIVITY");
        }

        // Rule 4: Suspicious round high-dollar transactions
        if (amount > 1000.0 && amount % 1000.0 == 0.0) {
            score += 10;
            assessment.rulesTriggered.add("ROUND_AMOUNT_STRUCTURING_CHECK");
        }

        // Cap score at 100
        assessment.riskScore = Math.min(score, 100);

        if (assessment.riskScore >= 75) {
            assessment.riskLevel = "CRITICAL";
            assessment.status = "REJECTED";
            assessment.recommendation = "Transaction auto-blocked. Escalate to Compliance & Risk Officer.";
        } else if (assessment.riskScore >= 40) {
            assessment.riskLevel = "HIGH";
            assessment.status = "FLAGGED";
            assessment.recommendation = "Transaction held for secondary manual manager review.";
        } else if (assessment.riskScore >= 20) {
            assessment.riskLevel = "MEDIUM";
            assessment.status = "APPROVED";
            assessment.recommendation = "Approved with audit trail logging.";
        } else {
            assessment.riskLevel = "LOW";
            assessment.status = "APPROVED";
            assessment.recommendation = "Standard transaction verified successfully.";
        }

        return assessment;
    }

    private static String escape(String s) {
        if (s == null) return "";
        return s.replace("\"", "\\\"");
    }

    public static void main(String[] args) {
        // Usage: java FraudDetectionService <refId> <type> <amount> <accType> <status> <dailyTxnCount>
        if (args.length < 6) {
            System.out.println("{\"error\": \"Usage: java FraudDetectionService <refId> <type> <amount> <accType> <status> <dailyTxnCount>\"}");
            return;
        }

        try {
            String refId = args[0];
            String type = args[1];
            double amount = Double.parseDouble(args[2]);
            String accType = args[3];
            String status = args[4];
            int dailyTxnCount = Integer.parseInt(args[5]);

            RiskAssessment result = analyzeTransaction(refId, type, amount, accType, status, dailyTxnCount);

            StringBuilder sb = new StringBuilder();
            sb.append("{\n");
            sb.append("  \"status\": \"success\",\n");
            sb.append("  \"engine\": \"Java 25 Enterprise Fraud Engine\",\n");
            sb.append("  \"reference_id\": \"").append(escape(result.referenceId)).append("\",\n");
            sb.append("  \"decision\": \"").append(result.status).append("\",\n");
            sb.append("  \"risk_score\": ").append(result.riskScore).append(",\n");
            sb.append("  \"risk_level\": \"").append(result.riskLevel).append("\",\n");
            sb.append("  \"recommendation\": \"").append(escape(result.recommendation)).append("\",\n");
            sb.append("  \"rules_triggered\": [\n");
            for (int i = 0; i < result.rulesTriggered.size(); i++) {
                sb.append("    \"").append(escape(result.rulesTriggered.get(i))).append("\"");
                if (i < result.rulesTriggered.size() - 1) sb.append(",");
                sb.append("\n");
            }
            sb.append("  ],\n");
            sb.append("  \"timestamp\": \"").append(Instant.now().toString()).append("\"\n");
            sb.append("}\n");

            System.out.println(sb.toString());

        } catch (Exception e) {
            System.out.println("{\"error\": \"" + escape(e.getMessage()) + "\"}");
        }
    }
}

