INSERT INTO auditevents (EventTimestamp, FunctionalityID, EventTypeID, StoreLocationID, CompanyId, UserName, Message, Status, AdditionalData) 
VALUES 
('2025-09-01 10:15:00', 1, 1, 45, 17, 'jdoe', 'User logged in successfully', 'Success', '{"ip":"192.168.1.10"}'),
('2025-09-01 10:20:00', 2, 1, 45, 17, 'asmith', 'Invalid password attempt', 'Failed', '{"ip":"192.168.1.11"}'),
('2025-09-02 09:05:00', 1, 2, 45, 17, 'mjones', 'New item added to inventory', 'Success', '{"itemId":12345}'),
('2025-09-02 09:30:00', 2, 2, 45, 17, 'mjones', 'Item updated successfully', 'Success', '{"itemId":12345}'),
('2025-09-02 09:40:00', 1, 2, 45, 17, 'mjones', 'Item deletion failed', 'Failed', '{"itemId":54321}'),
('2025-09-03 14:00:00', 2, 3, 45, 17, 'akhan', 'Invoice generated', 'Success', '{"invoiceId":9001}'),
('2025-09-03 14:10:00', 1, 3, 45, 17, 'akhan', 'Invoice creation failed', 'Failed', '{"invoiceId":9002}'),
('2025-09-04 11:25:00', 2, 4, 45, 17, 'rpatel', 'Sale transaction processed', 'Success', '{"transactionId":45001}'),
('2025-09-04 11:30:00', 1, 4, 45, 17, 'rpatel', 'Card declined', 'Failed', '{"transactionId":45002}'),
('2025-09-05 16:45:00', 2, 1, 45, 17, 'jdoe', 'User logged out', 'Success', '{"ip":"192.168.1.10"}'),
('2025-09-06 08:00:00', 1, 4, 45, 17, 'asmith', 'Report generated successfully', 'Success', '{"reportId":"sales-2025"}'),
('2025-09-06 08:15:00', 2, 4, 45, 17, 'asmith', 'Report generation failed', 'Failed', '{"reportId":"stock-2025"}'),
('2025-09-07 12:05:00', 1, 1, 45, 17, 'admin', 'New user created', 'Success', '{"newUser":"twhite"}'),
('2025-09-07 12:20:00', 2, 1, 45, 17, 'admin', 'User creation failed', 'Failed', '{"newUser":"gblack"}'),
('2025-09-08 13:50:00', 1, 2, 45, 17, 'system', 'Token validation passed', 'Success', '{"token":"abc123"}'),
('2025-09-08 13:55:00', 2, 2, 45, 17, 'system', 'Token expired', 'Failed', '{"token":"xyz789"}'),
('2025-09-09 15:10:00', 1, 3, 45, 17, 'syncsvc', 'POS sync completed', 'Success', '{"records":150}'),
('2025-09-09 15:15:00', 2, 3, 45, 17, 'syncsvc', 'POS sync failed', 'Failed', '{"records":0}'),
('2025-09-10 17:40:00', 1, 4, 45, 17, 'mailer', 'Email sent successfully', 'Success', '{"to":"customer@example.com"}'),
('2025-09-10 17:50:00', 2, 4, 45, 17, 'mailer', 'Email delivery failed', 'Failed', '{"to":"customer2@example.com"}');

-----------------------------------------------------

--Request body:
{
  "event_timestamp": "2025-09-12T08:39:28.909Z",
  "functionality": "string",
  "event_type": "string",
  "store_id": 0,
  "company_id": 0,
  "user": "string",
  "message": "string",
  "status": "Success",
  "additional_data": {}
}
-----------------------------------------------------
--Examples:

{
  "event_timestamp": "2025-09-01T17:18:06.561Z",
  "functionality": "test",
  "event_type": "test",
  "store_id": 12,
  "company_id": 13,
  "user": "test",
  "message": "This is test message",
  "status": "Success",
  "additional_data": {
    "transaction_id": "TX789456",
    "amount": 156.75,
    "items_count": 5
  }
}

--Transaction Event
{
  "event_timestamp": "2025-09-29T06:26:58.706Z",
  "functionality": "Sales",
  "event_type": "Transaction",
  "store_id": 101,
  "company_id": 1,
  "user": "john.doe",
  "message": "Completed sales transaction",
  "status": "Success",
  "additional_data": {
    "transaction_id": "TX123456",
    "amount": 250.50,
    "items_count": 4,
    "payment_method": "credit_card"
  }
}


--Login Attempt
{
  "event_timestamp": "2025-09-01T09:30:00Z",
  "functionality": "Authentication",
  "event_type": "Login",
  "store_id": null,
  "company_id": 17,
  "user": "saqa",
  "message": "User logged in successfully",
  "status": "Success",
  "additional_data": {
    "ip_address": "192.168.1.101",
    "user_agent": "Chrome/120.0"
  }
}


--Failed Login Attempt
{
  "event_timestamp": "2025-09-01T09:45:00Z",
  "functionality": "Authentication",
  "event_type": "Login",
  "store_id": null,
  "company_id": 1,
  "user": "bob.jones",
  "message": "Invalid credentials provided",
  "status": "Failed",
  "additional_data": {
    "ip_address": "192.168.1.102",
    "attempt_count": 3
  }
}


--System Configuration Change
{
  "event_timestamp": "2025-09-01T17:27:56.784Z",
  "functionality": "System",
  "event_type": "Configuration",
  "store_id": null,
  "company_id": 1,
  "user": "admin",
  "message": "Updated system settings",
  "status": "Success",
  "additional_data": {
    "previous_values": {"max_users": 50, "timeout": 30},
    "changed_settings": ["timeout"]
  }
}



