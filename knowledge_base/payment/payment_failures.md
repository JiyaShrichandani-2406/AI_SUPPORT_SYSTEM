# Payment Failures

## Metadata

Title: Handling Payment Failures
Product: PayPal
Product Version: Current PayPal Orders and Payments APIs
Source Type: Official Documentation
Source Organization: PayPal Developer
Topic: Payment Failures and Recovery
Source URL: https://developer.paypal.com/api/handle-payment-failures/
Last Updated: June 10, 2026
Collected On: September 19, 2026

## Problem / Overview

A payment failure occurs when a payment cannot be completed,
authorized, captured, or processed successfully.

Payment failures can occur for different reasons, including declined
payment methods, expired payment methods, insufficient funds, risk
restrictions, invalid request data, authentication failures, and
business validation errors.

PayPal APIs return error codes and messages that can be used to
identify the type of failure and determine an appropriate response.

Some payment failures may also occur asynchronously and may not be
immediately visible during the initial transaction.

## Symptoms

Common payment-failure symptoms include:

- Payment is declined.
- Payment method is expired.
- Payment cannot be captured.
- Buyer cannot complete the transaction.
- Payment request contains invalid data.
- Currency is not supported.
- Payment attempts exceed the allowed number.
- API authentication fails.
- The requested payment resource cannot be found.
- Payment is denied because of account or risk restrictions.

## Common Causes

According to PayPal's official documentation, payment failures can
result from:

- Declined payment instruments.
- Expired cards or payment methods.
- Insufficient funds.
- Unsupported currencies.
- Invalid or missing request data.
- Amount mismatches.
- Item-total mismatches.
- Authentication failures.
- Authorization failures.
- Payment-method restrictions.
- Risk restrictions.
- Too many failed payment attempts.
- Invalid or missing resources.
- Server-side or processing errors.

## Diagnostic Steps

### 1. Inspect the API Response

Always inspect the response from the relevant PayPal API operation.

Identify:

- Error code
- Error message
- HTTP status
- Debug ID when available
- Additional error details

### 2. Check for a Declined Payment

For example:

`INSTRUMENT_DECLINED`

indicates that the payment instrument was declined.

The buyer may need to select another payment method.

### 3. Check Expired Payment Methods

For example:

`CARD_EXPIRED`

indicates that the card has expired.

The buyer should use an appropriate valid payment method.

### 4. Check Amount Errors

Errors such as:

`AMOUNT_MISMATCH`

or

`ITEM_TOTAL_MISMATCH`

indicate that the amounts in the request do not correctly correspond.

Review the order amounts, item totals, taxes, discounts, and other
relevant values.

### 5. Check Currency

For:

`CURRENCY_NOT_SUPPORTED`

verify that the currency is supported by the payment method and
account configuration.

### 6. Check Authentication

For:

`AUTHENTICATION_FAILURE`

verify that the API credentials are correct and that the integration
is using the appropriate authentication configuration.

### 7. Check Authorization

For:

`NOT_AUTHORIZED`

verify that the API caller has the permissions required to perform
the requested operation.

### 8. Check Validation Errors

For:

`VALIDATION_ERROR`

or

`UNPROCESSABLE_ENTITY`

review the request data and verify that required fields are present
and contain valid values.

### 9. Check Resource Errors

For:

`RESOURCE_NOT_FOUND`

verify that the requested resource ID exists and is correct.

### 10. Check Logs and Webhooks

Log failed payment attempts with their error codes and messages.

For asynchronous payment events, monitor the appropriate PayPal
webhook events.

## Resolution / Recommended Actions

- Ask the buyer to use another payment method when the payment
  instrument is declined.
- Ask the buyer to use a valid payment method when the existing
  payment method has expired.
- Correct amount or item-total mismatches in the API request.
- Use a supported currency.
- Correct missing or invalid request parameters.
- Verify API credentials when authentication fails.
- Verify account permissions when authorization fails.
- Correct invalid resource IDs.
- Review risk or account restrictions when the payment is denied.
- Avoid unnecessary repeated payment attempts.
- Log error codes and relevant diagnostic information.
- Monitor webhook events for asynchronous payment failures.
- Test payment-failure scenarios in the PayPal sandbox environment.

## Important Notes / Limitations

- A payment failure does not have a single universal cause.
- The exact error code and API response should be examined before
  selecting a resolution.
- Some payment failures are asynchronous and may occur after the
  initial payment request.
- Payment-method availability can vary depending on the buyer,
  country, account, and payment method.
- Payment failures related to risk or account restrictions may require
  additional investigation or support.
- Do not store card numbers, CVV values, passwords, access tokens,
  API secrets, or other sensitive payment information in the
  Knowledge Base.

## Source

PayPal Developer Official Documentation:

1. Handling Payment Failures
   https://developer.paypal.com/api/handle-payment-failures/

2. Common Errors Overview
   https://developer.paypal.com/api/errors/overview/

3. Handling API Responses
   https://developer.paypal.com/api/handle-api-responses/

4. Validation Error
   https://developer.paypal.com/api/errors/validation-error