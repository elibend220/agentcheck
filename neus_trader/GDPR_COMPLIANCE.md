# GDPR Compliance & Privacy Policy

**Last Updated**: August 2026  
**Version**: 1.0  
**Regulatory Requirement**: EU Regulation 2016/679

---

## 1. Controller & Data Protection Officer

**Data Controller**: NEUS Trader Inc.  
**Privacy Contact**: privacy@neus-trader.io  
**Registered Address**: [Company jurisdiction]

---

## 2. Privacy Principles (GDPR Article 5)

NEUS Trader adheres to all GDPR principles in personal data processing:

| Principle | Implementation |
|-----------|-----------------|
| **Lawfulness** | Processing only with valid legal basis documented |
| **Fairness** | Transparent practices, no deceptive processing |
| **Transparency** | Privacy notice provided before any processing |
| **Purpose Limitation** | Data used only for stated trading purpose |
| **Data Minimization** | Only necessary data for trading collected |
| **Accuracy** | Data kept current, users can correct errors |
| **Storage Limitation** | Trade data 7 years (regulatory), then deleted |
| **Integrity/Confidentiality** | Encryption, access controls, audit logging |

---

## 3. Legal Bases for Processing (GDPR Article 6)

### 3.1 Consent (Article 6(1)(a))
- Users explicitly consent to data processing for trading
- Consent is separate from trading agreement
- Users can withdraw consent at any time
- Consent records kept for 7 years

### 3.2 Contract (Article 6(1)(b))
- Processing necessary to execute trading agreement
- Order data, fills, and performance metrics
- Required for fulfillment of trading services

### 3.3 Legal Obligation (Article 6(1)(c))
- Tax/regulatory reporting requirements
- 7-year record retention for trading data
- AML/KYC compliance with exchange

---

## 4. Data Categories & Collection

### 4.1 Account Information
- Email address (encrypted at rest)
- Timezone/location preference
- API key (hashed, never stored plaintext)
- Account creation date

**Basis**: Consent + Contract  
**Retention**: 1 year after account closure  
**User Control**: Can correct, request export, request deletion

### 4.2 Trading Data
- Symbols traded (BTC, ETH, etc.)
- Order size and entry/exit prices
- Profit/loss per trade
- Timestamps of all trades
- Risk metrics (drawdown, Sharpe ratio)

**Basis**: Contract + Legal Obligation  
**Retention**: 7 years (regulatory requirement)  
**User Control**: Can export, analyze own data

### 4.3 System & Performance Data
- API requests (rate limiting)
- System uptime/performance
- Backtest results (pseudonymized)
- Error logs (stripped of PII)

**Basis**: Legitimate Interests  
**Retention**: 90 days for error logs  
**User Control**: Limited (for system improvement)

### 4.4 Audit & Compliance Data
- Login timestamps and IP (hashed)
- Configuration changes
- Security events
- Audit trail

**Basis**: Legal Obligation  
**Retention**: 7 years  
**User Control**: Can request their audit entries

---

## 5. Data Subject Rights (GDPR Articles 12-22)

### 5.1 Right to Access (Article 15)
**You can request**:
- All personal data we hold about you
- Purpose of processing
- Data recipients
- Retention period

**How to Request**: privacy@neus-trader.io  
**Response Time**: 30 days  
**Format**: JSON or CSV export via API

```bash
# Example: Request your data
curl -X GET https://api.neus-trader.io/user/data \
  -H "Authorization: Bearer <your_token>"
```

### 5.2 Right to Rectification (Article 16)
**You can correct**:
- Inaccurate email address
- Timezone/location
- Any other profile information

**How to Request**: PATCH /user/profile or email privacy@neus-trader.io

### 5.3 Right to Erasure (Article 17)
**We will delete**:
- Account profile
- Personal settings
- Non-regulatory data

**We will retain** (cannot delete due to law):
- Trade records (7 years for tax)
- Audit logs (7 years for compliance)

**How to Request**: DELETE /user or email privacy@neus-trader.io  
**Processing Time**: 30 days  
**Note**: Regulatory data pseudonymized if possible

### 5.4 Right to Restrict Processing (Article 18)
**You can restrict**:
- Marketing communications
- Data usage for system improvement
- Performance analytics

**How to Request**: PATCH /user/preferences or email privacy@neus-trader.io

### 5.5 Right to Data Portability (Article 20)
**You can export your data in**:
- JSON format (all trading data)
- CSV format (trade history)
- Compatible with other platforms

**How to Request**: GET /user/export (returns zip file)

### 5.6 Right to Object (Article 21)
**You can opt-out of**:
- Marketing emails
- Performance improvement analytics
- Non-essential processing

### 5.7 Right to Withdraw Consent (Article 7(3))
**You can withdraw**:
- Trading authorization
- Consent to email communications
- Any other explicit consent

**Effect**: We stop processing immediately (except legal obligations)

---

## 6. Data Retention Schedule

| Data Category | Retention Period | Legal Requirement | Deletion Method |
|---------------|-----------------|------------------|-----------------|
| Account Profile | 1 year after closure | GDPR Art. 5 | Secure deletion |
| Trade Records | 7 years | Tax regulation | Archived/encrypted |
| Audit Logs | 7 years | Regulatory | Immutable storage |
| Session Tokens | 24 hours max | Security | Automatic expiry |
| Error Logs | 90 days | System ops | Secure deletion |
| Marketing Data | 2 years | GDPR consent | Upon withdrawal |

---

## 7. Data Protection Measures (GDPR Article 32)

### 7.1 Encryption
- **At Rest**: AES-256 encryption with PBKDF2 key derivation
- **In Transit**: TLS 1.3 (minimum) for all communications
- **Key Management**: Rotation every 365 days

### 7.2 Access Control
- Multi-factor authentication (TOTP)
- Role-based access control (RBAC)
- API key authentication with rate limiting
- IP address whitelisting available

### 7.3 Audit & Monitoring
- Immutable audit logs (7-year retention)
- Real-time security monitoring
- Anomaly detection (failed logins, unusual activity)
- Monthly security metrics review

### 7.4 Testing & Assessment
- Quarterly penetration testing
- Annual SOC 2 Type II audit
- Weekly dependency vulnerability scanning
- Monthly static code analysis (SAST)

---

## 8. Data Transfers & Third Parties

### 8.1 Sub-processors (Article 28)
We use the following sub-processors for data handling:

| Sub-processor | Purpose | Data | Agreement |
|---------------|---------|------|-----------|
| **Binance** | Order execution | Trading data | Data Processing Agreement |
| **AWS** | Cloud storage | Encrypted backups | Data Processing Agreement |
| **Cloudflare** | DDoS protection | IP logs (temporary) | Data Processing Agreement |

### 8.2 International Transfers
- No data transfers outside user's jurisdiction
- All processing in-region
- If needed: Standard Contractual Clauses (SCC) used per GDPR Chapter V

### 8.3 Law Enforcement Requests
- We comply with lawful legal requests only
- We notify users when legally permitted
- We retain copies for audit trail

---

## 9. Data Breach Notification (GDPR Articles 33-34)

### 9.1 Breach Definition
Loss of confidentiality, integrity, or availability of personal data

### 9.2 Notification Procedure
**Supervisor Notification**: Within 72 hours of discovery  
**User Notification**: Without undue delay if high risk  
**Affected Users**: Notified by email + in-app alert

### 9.3 Breach Contact
Report suspected breach to: security@neus-trader.io

---

## 10. Cookie & Tracking Policy

### 10.1 Essential Cookies
- Session tokens (authentication)
- CSRF tokens (security)
- User preferences

**Legal Basis**: Contract (necessary for service)

### 10.2 Analytics Cookies
- None - we don't use third-party tracking

### 10.3 Your Cookie Rights
- Accept/reject in settings
- Clear cookies anytime
- Disable cookies in browser

---

## 11. Automated Decision-Making (GDPR Article 22)

NEUS Trader **does not** use automated decision-making for:
- Account termination
- Performance evaluation
- Limiting trading access

**You have the right to**:
- Request human review of any system decision
- Explain system reasoning
- Challenge automated outcomes

---

## 12. Privacy by Design

NEUS Trader implements privacy by design (GDPR Article 25):

- ✅ Data minimization at collection
- ✅ Pseudonymization where possible
- ✅ Encryption defaults
- ✅ User consent required
- ✅ Privacy settings enabled by default
- ✅ Regular impact assessments

---

## 13. Data Protection Impact Assessment (DPIA)

We conduct DPIA for:
- New trading features (market hour filtering, position sizing)
- Risk management changes
- Data collection expansions
- Security measure updates

**Latest DPIA**: [Date]  
**Next DPIA**: [Date + 12 months]

---

## 14. Complaints & Escalation

### 14.1 Internal Escalation
1. Contact privacy@neus-trader.io (response within 30 days)
2. Request escalation to Data Protection Officer
3. Request full investigation & remediation

### 14.2 Regulatory Complaint
**Right**: You can lodge complaint with national data protection authority

**Example Authorities**:
- 🇪🇺 EU: National Data Protection Authority
- 🇩🇪 Germany: Bundesbeauftragte für Datenschutz
- 🇬🇧 UK: Information Commissioner's Office (ICO)

---

## 15. Frequently Asked Questions

### Q: How long do you keep my trade data?
**A**: 7 years (required by tax regulation). After 7 years, data is securely deleted.

### Q: Can I export all my data?
**A**: Yes! Use GET /user/export or email privacy@neus-trader.io for JSON/CSV export.

### Q: What if I want to delete my account?
**A**: Use DELETE /user or email privacy@neus-trader.io. Account profile deleted within 30 days. Trade records kept 7 years for tax compliance.

### Q: Do you sell my data?
**A**: No. We never sell or share personal data for marketing or third-party purposes.

### Q: Is my data encrypted?
**A**: Yes. All sensitive data encrypted with AES-256 at rest, TLS 1.3 in transit.

### Q: How do you handle breach?
**A**: We notify supervisors within 72 hours and affected users immediately (if high risk).

---

## 16. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Aug 2026 | Initial ISO 27001 + GDPR compliance |

---

**Last Updated**: August 2026  
**Next Review**: November 2026

For questions: privacy@neus-trader.io  
For complaints: compliance@neus-trader.io
