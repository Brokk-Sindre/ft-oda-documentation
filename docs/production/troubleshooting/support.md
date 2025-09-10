# Getting Support

Get help with the Danish Parliamentary OData API through various support channels and resources.

## Support Overview

The Danish Parliamentary OData API provides multiple avenues for getting support, from self-service resources to direct contact channels. This guide covers all available support options and best practices for getting effective help.

### Available Support Channels

| Channel | Response Time | Best For |
|---------|--------------|----------|
| Documentation | Immediate | API reference, examples, common issues |
| Community Forums | 1-3 business days | General questions, sharing solutions |
| GitHub Issues | 3-5 business days | Bug reports, feature requests |
| Technical Support | 1-2 business days | Complex technical issues |
| Emergency Contact | Same day | Critical production issues |

## Self-Service Resources

### Primary Documentation

Start with these comprehensive resources:

- **[API Reference](/api-reference/)** - Complete entity documentation and endpoints
- **[Getting Started Guide](/getting-started/)** - Quick setup and first queries
- **[Common Mistakes](/getting-started/common-mistakes/)** - Avoid frequent pitfalls
- **[Troubleshooting Guide](/production/troubleshooting/)** - Diagnostic procedures

### Interactive Tools

Use our built-in tools for immediate help:

- **Query Builder** - Test API queries in real-time
- **Response Viewer** - Analyze API responses and formats
- **Error Code Lookup** - Understand HTTP status codes and error messages

### Code Examples

Access working examples in multiple languages:

- **[Python Examples](/code-examples/python/)** - Complete client implementations
- **[JavaScript Examples](/code-examples/javascript/)** - Browser and Node.js usage
- **[TypeScript Examples](/code-examples/typescript/)** - Type-safe implementations
- **[cURL Examples](/code-examples/curl/)** - Command-line testing

## Community Support

### Discussion Forums

Join the active developer community:

**GitHub Discussions**: [oda.ft.dk/discussions](https://github.com/Folketinget/oda-api/discussions)
- General questions and answers
- Best practices sharing
- Feature discussions
- Community-driven solutions

**Stack Overflow**: Tag your questions with `danish-parliament-api`
- Technical implementation questions
- Code-level troubleshooting
- Integration challenges

### Community Guidelines

When participating in community forums:

1. **Search first** - Check if your question has been answered
2. **Be specific** - Provide exact error messages and query examples
3. **Share solutions** - Help others by documenting your fixes
4. **Follow up** - Mark questions as resolved when fixed

## Knowledge Base Resources

### Comprehensive Guides

- **[Performance Optimization](/production/performance/)** - Query efficiency and scaling
- **[Security Best Practices](/production/security/)** - Safe API usage
- **[Data Model Documentation](/data-model/)** - Understanding parliamentary processes
- **[Compliance Information](/compliance/)** - GDPR, licensing, data quality

### Quick Reference

- **[HTTP Error Codes](/api-reference/errors/http-codes/)** - Status code meanings
- **[OData Query Parameters](/api-reference/odata/)** - Filter, sort, expand options
- **[Entity Relationships](/data-model/entity-relationships/)** - How data connects

## Issue Reporting

### Bug Reports

Report bugs through GitHub Issues: [oda.ft.dk/issues](https://github.com/Folketinget/oda-api/issues)

**Required Information**:
```
- API endpoint affected
- Query parameters used
- Expected vs actual behavior
- Error messages (exact text)
- Timestamp of issue
- Client implementation details
```

**Bug Report Template**:
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Call endpoint: GET https://oda.ft.dk/api/...
2. With parameters: $filter=...
3. Observe error: ...

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened

## Environment
- Client: Python 3.11 / JavaScript / cURL
- Library version: requests 2.31.0
- Timestamp: 2024-01-15 14:30:00 UTC
- Query: [full URL with parameters]

## Additional Context
Any other relevant information
```

### Feature Requests

Submit enhancement requests with:

- **Use case description** - Why you need this feature
- **Proposed solution** - How it might work
- **Impact assessment** - Who would benefit
- **Alternative approaches** - Other ways you've tried

## Service Level Agreements

### Response Time Expectations

| Issue Severity | Initial Response | Resolution Target |
|----------------|------------------|-------------------|
| Critical (API down) | 2 hours | 24 hours |
| High (major functionality) | 8 hours | 3 business days |
| Medium (minor issues) | 1 business day | 5 business days |
| Low (enhancements) | 3 business days | Best effort |

### Severity Definitions

**Critical**: Complete API unavailability or data corruption
**High**: Major functionality broken, significant user impact
**Medium**: Minor functionality issues, workarounds available
**Low**: Feature requests, documentation improvements

## Escalation Procedures

### For Critical Issues

If the API is completely unavailable or returning incorrect data:

1. **Check API Status**: [status.oda.ft.dk](https://status.oda.ft.dk)
2. **Report Immediately**: Use emergency contact procedures
3. **Document Impact**: Business impact, affected users, timeline
4. **Follow Up**: Monitor status page for updates

### Escalation Path

```
Level 1: Community Support & Documentation
     (No resolution within SLA)
Level 2: GitHub Issues & Technical Support
     (Critical issues or SLA breach)
Level 3: Emergency Contact & Management
     (System-wide outages)
Level 4: Parliamentary IT Department
```

## Emergency Contact

### Critical Issues Only

For system-wide outages or data integrity issues:

**Email**: api-emergency@ft.dk
**Phone**: +45 33 37 55 00 (24/7 emergency line)
**Status Page**: [status.oda.ft.dk](https://status.oda.ft.dk)

### When to Use Emergency Contact

- Complete API unavailability (>1 hour)
- Data corruption or integrity issues
- Security incidents or breaches
- Legal compliance emergencies

**Do NOT use for**:
- Implementation questions
- Feature requests
- Non-critical bugs
- Performance optimization

## Effective Support Requests

### Before Contacting Support

1. **Reproduce the issue** consistently
2. **Check documentation** for similar problems
3. **Search community forums** for existing solutions
4. **Gather diagnostic information** (logs, queries, responses)
5. **Prepare minimal test case** that demonstrates the issue

### Information to Include

**Always Provide**:
- Exact API endpoint and full URL
- Complete error messages
- Timestamp of the issue
- Your implementation environment
- What you were trying to achieve

**Example Good Request**:
```
Subject: HTTP 500 error on Sag entity with complex filter

I'm getting a 500 Internal Server Error when querying the Sag 
entity with this filter:

URL: https://oda.ft.dk/api/Sag?$filter=titel%20eq%20'Forslag%20til%20lov%20om'%20and%20typeid%20eq%203

Error Response:
{
  "error": {
    "code": "InternalServerError",
    "message": "An error occurred while processing this request."
  }
}

Timestamp: 2024-01-15 14:30:00 UTC
Client: Python requests 2.31.0
Expected: List of Sag entities matching the filter
Actual: HTTP 500 error

Simple filters work fine, but this specific combination fails.
I've tried URL encoding different ways with the same result.
```

### What NOT to Include

- Sensitive personal information
- Complete database dumps
- Unrelated error messages
- Vague descriptions like "it doesn't work"

## Contributing to Community Knowledge

### Documentation Improvements

Help improve the documentation:

1. **GitHub Pull Requests**: [oda.ft.dk/docs](https://github.com/Folketinget/oda-docs)
2. **Report Documentation Issues**: Missing or incorrect information
3. **Suggest Examples**: Real-world use cases and code samples
4. **Translation Help**: Danish to English clarifications

### Sharing Solutions

When you solve a problem:

1. **Answer community questions** with similar issues
2. **Create blog posts** about complex implementations
3. **Share code examples** on GitHub
4. **Update documentation** with lessons learned

### Knowledge Base Contributions

**Accepted Contributions**:
- Code examples and snippets
- Use case documentation
- Performance optimization tips
- Integration patterns
- Troubleshooting guides

**Contribution Process**:
1. Fork the documentation repository
2. Create feature branch: `git checkout -b improve-troubleshooting`
3. Make changes with clear commit messages
4. Submit pull request with description
5. Respond to review feedback

### Recognition Program

Contributors receive recognition through:
- GitHub contributor badges
- Documentation credits
- Community spotlight features
- Direct feedback to parliamentary IT team

## Support Quality Feedback

Help us improve support by providing feedback:

**Support Survey**: [feedback.oda.ft.dk](https://feedback.oda.ft.dk)
**Direct Email**: support-feedback@ft.dk

Rate your experience and suggest improvements for:
- Documentation clarity
- Response times
- Solution effectiveness
- Community helpfulness

---

**Need immediate help?** Start with our [troubleshooting guide](/production/troubleshooting/) or check the [common mistakes](/getting-started/common-mistakes/) section.