---
title: Feedback - Help Improve Danish Parliament API Documentation
description: Provide feedback to help improve the Danish Parliament API documentation. Report issues, suggest improvements, or share your use cases.
keywords: feedback, documentation improvement, api suggestions, user input
---

# Feedback & Support

Help us improve the Danish Parliament API documentation! Your feedback is invaluable for making this resource better for everyone.

## Quick Feedback

<div class="feedback-widget">
  <h3>Was this documentation helpful?</h3>
  <div class="feedback-buttons">
    <button class="feedback-btn positive" onclick="submitQuickFeedback('positive')">
      👍 Yes, very helpful
    </button>
    <button class="feedback-btn negative" onclick="submitQuickFeedback('negative')">
      👎 Could be improved
    </button>
  </div>
  <div id="feedback-followup" style="display: none;">
    <textarea id="feedback-details" placeholder="Tell us more about what could be improved..."></textarea>
    <button onclick="submitDetailedFeedback()">Submit Feedback</button>
  </div>
  <div id="feedback-thanks" style="display: none;">
    <p>Thank you for your feedback! 🙏</p>
  </div>
</div>

## Detailed Feedback Form

### Report an Issue

Found a problem? Help us fix it:

- **Documentation Error**: Incorrect information or broken examples
- **Technical Issue**: Broken links, formatting problems, or loading issues  
- **API Problem**: Issues with the actual oda.ft.dk API
- **Missing Information**: Content gaps or incomplete sections

<div class="form-group">
  <label for="issue-type">Issue Type:</label>
  <select id="issue-type">
    <option value="">Select issue type</option>
    <option value="documentation-error">Documentation Error</option>
    <option value="technical-issue">Technical Issue</option>
    <option value="api-problem">API Problem</option>
    <option value="missing-info">Missing Information</option>
    <option value="other">Other</option>
  </select>
</div>

<div class="form-group">
  <label for="page-url">Page URL (if applicable):</label>
  <input type="url" id="page-url" placeholder="https://...">
</div>

<div class="form-group">
  <label for="issue-description">Description:</label>
  <textarea id="issue-description" placeholder="Describe the issue in detail..."></textarea>
</div>

<div class="form-group">
  <label for="expected-behavior">Expected Behavior:</label>
  <textarea id="expected-behavior" placeholder="What should happen instead?"></textarea>
</div>

<button onclick="submitIssueReport()" class="submit-btn">Report Issue</button>

### Suggest Improvements

Have ideas to make the documentation better?

<div class="form-group">
  <label for="improvement-type">Improvement Type:</label>
  <select id="improvement-type">
    <option value="">Select improvement type</option>
    <option value="new-content">New Content/Examples</option>
    <option value="better-explanation">Better Explanations</option>
    <option value="navigation">Navigation/Structure</option>
    <option value="design">Design/Usability</option>
    <option value="performance">Performance</option>
    <option value="mobile">Mobile Experience</option>
  </select>
</div>

<div class="form-group">
  <label for="improvement-description">Suggestion:</label>
  <textarea id="improvement-description" placeholder="Describe your improvement idea..."></textarea>
</div>

<div class="form-group">
  <label for="use-case">Your Use Case:</label>
  <textarea id="use-case" placeholder="How do you use the Danish Parliament API? This helps us prioritize improvements."></textarea>
</div>

<button onclick="submitImprovement()" class="submit-btn">Submit Suggestion</button>

### Share Your Use Case

We'd love to hear how you're using the Danish Parliament API!

<div class="form-group">
  <label for="project-description">Project Description:</label>
  <textarea id="project-description" placeholder="Tell us about your project or research..."></textarea>
</div>

<div class="form-group">
  <label for="project-url">Project URL (optional):</label>
  <input type="url" id="project-url" placeholder="https://...">
</div>

<div class="form-group">
  <label for="featured">Feature Permission:</label>
  <label class="checkbox-label">
    <input type="checkbox" id="featured">
    You may feature my project in the documentation (with credit)
  </label>
</div>

<button onclick="submitUseCase()" class="submit-btn">Share Use Case</button>

## Contact Information

### Direct Support
- **Email**: folketinget@ft.dk (subject: "Åbne Data")
- **Official API**: https://oda.ft.dk/

### Documentation Issues
- **GitHub Issues**: [Report technical problems](https://github.com/yourusername/ft/issues/new)
- **Pull Requests**: Contribute improvements directly

### Community
- **Discussions**: Share ideas and ask questions
- **Stack Overflow**: Tag questions with `danish-parliament-api`

## Response Time

We aim to respond to feedback within:
- **Critical Issues**: 24 hours
- **Bug Reports**: 2-3 business days  
- **Feature Requests**: 1 week
- **General Feedback**: 1-2 weeks

## Privacy Notice

Feedback submitted through this form:
- Is used solely to improve documentation
- May be shared anonymously with the Danish Parliament IT team
- Will not be used for marketing purposes
- Can be requested for deletion (email us)

Thank you for helping make this documentation better! 🇩🇰

<script>
function submitQuickFeedback(type) {
  // Track feedback in analytics
  if (typeof trackEvent !== 'undefined') {
    trackEvent('Feedback', 'quick_feedback', type, 1);
  }
  
  if (type === 'negative') {
    document.getElementById('feedback-followup').style.display = 'block';
  } else {
    document.getElementById('feedback-thanks').style.display = 'block';
    document.querySelector('.feedback-buttons').style.display = 'none';
  }
}

function submitDetailedFeedback() {
  const details = document.getElementById('feedback-details').value;
  
  if (typeof trackEvent !== 'undefined') {
    trackEvent('Feedback', 'detailed_feedback', 'negative_with_details', details.length);
  }
  
  // Here you would normally send to your feedback collection service
  console.log('Detailed feedback:', details);
  
  document.getElementById('feedback-followup').style.display = 'none';
  document.getElementById('feedback-thanks').style.display = 'block';
}

function submitIssueReport() {
  const issueType = document.getElementById('issue-type').value;
  const pageUrl = document.getElementById('page-url').value;
  const description = document.getElementById('issue-description').value;
  const expected = document.getElementById('expected-behavior').value;
  
  if (!issueType || !description) {
    alert('Please fill in the required fields (Issue Type and Description)');
    return;
  }
  
  if (typeof trackEvent !== 'undefined') {
    trackEvent('Feedback', 'issue_report', issueType, 1);
  }
  
  const issueData = {
    type: issueType,
    page: pageUrl,
    description: description,
    expected: expected,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };
  
  // Here you would send to your issue tracking system
  console.log('Issue reported:', issueData);
  
  alert('Thank you for reporting this issue! We\'ll investigate and respond via the documentation updates.');
  
  // Clear form
  document.getElementById('issue-type').value = '';
  document.getElementById('page-url').value = '';
  document.getElementById('issue-description').value = '';
  document.getElementById('expected-behavior').value = '';
}

function submitImprovement() {
  const type = document.getElementById('improvement-type').value;
  const description = document.getElementById('improvement-description').value;
  const useCase = document.getElementById('use-case').value;
  
  if (!type || !description) {
    alert('Please fill in the required fields (Improvement Type and Suggestion)');
    return;
  }
  
  if (typeof trackEvent !== 'undefined') {
    trackEvent('Feedback', 'improvement_suggestion', type, 1);
  }
  
  const suggestionData = {
    type: type,
    description: description,
    useCase: useCase,
    timestamp: new Date().toISOString()
  };
  
  console.log('Improvement suggested:', suggestionData);
  
  alert('Thank you for your suggestion! We\'ll consider it for future documentation updates.');
  
  // Clear form
  document.getElementById('improvement-type').value = '';
  document.getElementById('improvement-description').value = '';
  document.getElementById('use-case').value = '';
}

function submitUseCase() {
  const description = document.getElementById('project-description').value;
  const url = document.getElementById('project-url').value;
  const featured = document.getElementById('featured').checked;
  
  if (!description) {
    alert('Please describe your project');
    return;
  }
  
  if (typeof trackEvent !== 'undefined') {
    trackEvent('Feedback', 'use_case_shared', featured ? 'featured_allowed' : 'private', 1);
  }
  
  const useCaseData = {
    description: description,
    url: url,
    featured: featured,
    timestamp: new Date().toISOString()
  };
  
  console.log('Use case shared:', useCaseData);
  
  alert('Thank you for sharing your use case! This helps us understand how the API is being used.');
  
  // Clear form
  document.getElementById('project-description').value = '';
  document.getElementById('project-url').value = '';
  document.getElementById('featured').checked = false;
}
</script>

<style>
.feedback-widget {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid var(--md-primary-fg-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem 0;
  text-align: center;
}

.feedback-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin: 1rem 0;
}

.feedback-btn {
  background: var(--md-primary-fg-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.feedback-btn:hover {
  background: var(--md-primary-fg-color--dark);
  transform: translateY(-2px);
}

.feedback-btn.negative {
  background: #dc3545;
}

.feedback-btn.negative:hover {
  background: #c82333;
}

.form-group {
  margin: 1.5rem 0;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--md-primary-fg-color);
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--md-default-fg-color--lightest);
  border-radius: 6px;
  font-family: inherit;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--md-primary-fg-color);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.submit-btn {
  background: var(--md-primary-fg-color);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.2s;
  margin: 1rem 0 2rem 0;
}

.submit-btn:hover {
  background: var(--md-primary-fg-color--dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(198, 12, 48, 0.3);
}

#feedback-followup textarea {
  width: 100%;
  margin: 1rem 0 0.5rem 0;
  padding: 0.75rem;
  border-radius: 6px;
  border: 2px solid var(--md-default-fg-color--lightest);
  min-height: 100px;
}

#feedback-thanks {
  color: var(--api-success-color);
  font-weight: 600;
  font-size: 1.1rem;
}

@media screen and (max-width: 768px) {
  .feedback-buttons {
    flex-direction: column;
  }
  
  .feedback-btn {
    font-size: 0.9rem;
    padding: 0.6rem 1rem;
  }
}
</style>