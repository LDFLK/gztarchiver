# Integration Guide: DeepSeek API with WSO2 BIJIRA API Gateway

## Overview

This document provides comprehensive guidance for integrating the DeepSeek Large Language Model with the WSO2 BIJIRA API Gateway. The integration enables document categorization through the DeepSeek LLM while leveraging BIJIRA as an intermediary gateway rather than calling the DeepSeek API directly. This architecture provides enhanced security, monitoring capabilities, and centralized API management.

## Prerequisites

Before proceeding with the integration, ensure you have the following:

- A DeepSeek API account with valid API credentials
- Access to WSO2 BIJIRA Console
- Appropriate permissions to create and manage projects within your organization

## Step-by-Step Configuration

### Step 1: Account Access

Access the WSO2 BIJIRA Console by navigating to one of the following URLs based on your account status:

**New users (account creation):**
```
https://console.bijira.dev/signup
```

**Existing users (login):**
```
https://console.bijira.dev/login
```

### Step 2: Project Creation

Create a new project within your organization by navigating to the project creation page:

```
https://console.bijira.dev/organizations/{your-organisation-name}/projects/new
```

Replace `{your-organisation-name}` with your actual organization identifier.

### Step 3: Navigate to Project Dashboard

Access your newly created project. On the project dashboard, locate the Create button positioned adjacent to the architecture diagram. This button initiates the component creation workflow.

### Step 4: Component Creation Initiation

Select the Create button to begin configuring a new component. The system will redirect you to the component configuration interface:

```
https://console.bijira.dev/organizations/{your-organisation-name}/projects/{your-project-name}/components/new
```

### Step 5: Component Type Selection

The component configuration page presents two primary options:

- **API Proxy** – For proxying API calls through the BIJIRA gateway
- **MCP Server** – For Model Context Protocol server configuration

Select **API Proxy** to proceed with the LLM integration.

### Step 6: API Source Configuration

Within the API Proxy section, two subcategories are available:

- **My APIs (Ingress)** – For internal or organizational APIs
- **Third Party APIs (Egress)** – For external API integrations

Select **Third Party APIs (Egress)** as DeepSeek is an external service provider.

### Step 7: AI API Selection

The Third Party APIs section offers three integration methods:

- **Import API Contract** – Import OpenAPI or similar specifications
- **Browse APIs** – Explore available API templates
- **AI APIs** – Pre-configured artificial intelligence service integrations

Select **AI APIs** to access the collection of supported LLM providers.

### Step 8: API Template Configuration

The AI APIs section displays various pre-built integration templates. While DeepSeek is not explicitly listed, select **Mistral AI API** as it provides a compatible configuration framework for DeepSeek integration.

Configure the component with the following parameters:

| Parameter | Value |
|-----------|-------|
| Name | `deepseek` |
| Identifier | `deepseek` |
| Version | Maintain default value |
| Description | Custom description (optional) |
| Target | `https://api.deepseek.com/v1/chat/completions` |

Complete the configuration and create the component. The system will automatically redirect to the component overview page and deploy the component to the development environment.

### Step 9: API Security Configuration

Navigate to the policy configuration section to establish authentication parameters:

1. In the sidebar, locate and select **Policy** under the **Develop** section
2. Select **Settings** to access the configuration panel
3. Click **Configure** to modify security settings

Enter the following authentication credentials:

```
API Key Header: Authorization
API Key: Bearer {your-api-key}
```

Replace `{your-api-key}` with your actual DeepSeek API key. Save the configuration to apply the authentication settings to the gateway.

### Step 10: API Testing (Optional)

To verify the integration configuration, access the testing console:

1. Navigate to **Console** under the **Test** section in the sidebar
2. Execute test requests to validate the API proxy functionality

### Step 11: Environment Promotion

Promote the API component from the development environment to production:

1. Return to the component overview page
2. Initiate the promotion process to the production environment (or the appropriate critical environment as defined by your organization's deployment strategy)
3. When prompted for configuration type, select **Use Development endpoint configuration**
4. Confirm the promotion to complete the deployment

### Step 12: API Publication

Publish the API to make it accessible for consumption:

1. Navigate to **Lifecycle** under the **Deploy** section in the sidebar
2. The lifecycle status should display as **Created**
3. Click **Publish** to update the API status. The architecture diagram will reflect the published state.

### Step 13: Production Endpoint Access

Retrieve the production endpoint URL for integration into your application:

1. Locate the **Developer Portal** button in the upper-right corner of the interface
2. Select **Go to Devportal** to access the developer portal
3. The production endpoint URL will be displayed on the portal page

This production endpoint should replace the original DeepSeek API endpoint in your application code.

### Step 14: Application Creation and Subscription

Create an application and subscribe to the API:

1. In the Developer Portal sidebar, select **Applications**
2. Click the **Create** button and provide an application name
3. Navigate to the **APIs** tab in the sidebar to view available APIs
4. Locate the DeepSeek API component and click **Subscribe**
5. Return to the **Applications** tab and select your created application to view the subscription dashboard and associated endpoints

### Step 15: Access Token Generation

Generate API access credentials for the production endpoint:

1. Within the application dashboard, locate the **Manage Keys** button in the upper-right corner
2. Select the **Production** tab
3. Generate a new access key
4. Configure key parameters such as expiration time and access scopes as required

To retrieve the access token programmatically, use the cURL command available in the **Instructions** section:

```bash
curl -k -X POST <TOKEN_ENDPOINT_URL> -d "grant_type=client_credentials" -H "Authorization: Basic Base64(<CONSUMER_KEY>:<CONSUMER_SECRET>)"
```

### Step 16: Implementation and Monitoring

Complete the integration by updating your application:

1. Replace the original DeepSeek API endpoint with the BIJIRA production endpoint URL
2. Update authentication headers to use the generated access token
3. Monitor API usage, performance metrics, and analytics through the BIJIRA console dashboard

## Integration Benefits

Implementing the BIJIRA API Gateway provides several operational advantages:

- **Centralized API Management**: Unified control and governance of all API integrations across your organization
- **Enhanced Security**: Additional authentication layer and secure credential management
- **Monitoring and Analytics**: Real-time tracking of API calls, usage patterns, and performance metrics
- **Rate Limiting and Throttling**: Control and optimize API consumption to prevent overuse and manage costs
- **Environment Management**: Seamless promotion and deployment across development, staging, and production environments

## Additional Resources

For comprehensive documentation, advanced configuration options, and troubleshooting guidance, consult the official BIJIRA documentation:

[WSO2 BIJIRA Documentation](https://wso2.com/bijira/docs/)

---

*For technical support or implementation assistance, contact your organization's API management team or WSO2 support channels.*