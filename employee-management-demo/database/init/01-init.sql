-- Employee Management Database Initialization

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone to Vietnam
SET timezone = 'Asia/Ho_Chi_Minh';

-- Log completion
SELECT 'Employee Management Database initialized successfully!' as status;