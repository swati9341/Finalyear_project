# Supabase Integration

This project now uses a **Supabase-only database strategy**. All database operations are directed to Supabase.

## How It Works

The application directly interacts with Supabase for all data persistence. There are no fallback mechanisms to other databases (MySQL/SQLite) implemented in the backend code.

## Setup Instructions

### 1. Install Dependencies
Ensure `supabase` is in your `requirements.txt`.

```bash
pip install -r requirements.txt
```

The `supabase` package is now included in `requirements.txt`.

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure your Supabase credentials. These are **mandatory** for the application to function.

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
 
# For JWT token generation (mandatory for authentication)
SECRET_KEY=your_secret_key_for_jwt_generation_and_verification
ALGORITHM=HS256 # Common algorithm like HS256
```

### 3. Set Up Supabase Tables

You need to create tables in Supabase that match your SQLAlchemy models. Here's a quick guide:

#### Create `users` Table

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  password_hash TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

#### Create `invoice_items` Table

```sql
CREATE TABLE invoice_items (
  id BIGSERIAL PRIMARY KEY,
  invoice_id BIGINT,
  userId BIGINT NOT NULL,
  description TEXT,
  data TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (userId) REFERENCES users(id)
);

CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
```

#### Create `invoice_templates` Table

```sql
CREATE TABLE invoice_templates (
  id BIGSERIAL PRIMARY KEY,
  template_name TEXT NOT NULL,
  html_content TEXT NOT NULL,
  type TEXT NOT NULL,
  mandatory_params JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Usage in Routers

### Option 1: Using Helper Functions (Recommended)

Import the helper functions and use them in your routers:

```python
from utils.db_helpers import create_record, read_record, update_record, delete_record, list_records
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example: Create a user
@app.post("/users/")
def create_user(user_data: UserSchema, db: Session = Depends(get_db)):
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=user_data.password_hash
    )
    
    # Create with automatic Supabase fallback
    created_user = create_record(
        db,
        user,
        "users",
        user_data.dict()
    )
    
    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return created_user

# Example: Read a user
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = read_record(
        db,
        "users",
        user_id,
        lambda: db.query(User).filter(User.id == user_id).first()
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Example: Update a user
@app.put("/users/{user_id}")
def update_user(user_id: int, updates: UserUpdateSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = update_record(
        db,
        user,
        updates.dict(exclude_unset=True),
        "users",
        user_id
    )
    
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update user")
    
    return updated_user

# Example: Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_record(db, user, "users", user_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    
    return {"detail": "User deleted successfully"}

# Example: List users
@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    users = list_records(
        db,
        "users",
        lambda: db.query(User).all()
    )
    
    if users is None:
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    
    return users
```

### Option 2: Direct Database Fallback Usage

For more control, use the `database_fallback` module directly:

```python
from database_fallback import db_fallback

# Check if Supabase is available
if db_fallback.supabase_available:
    print("Supabase fallback is configured and ready")

# Use Supabase client directly for fallback operations
if db_fallback.supabase_available:
    user = db_fallback.supabase_fallback.get_by_id("users", user_id)
```

## Testing Fallback Behavior

To test the Supabase fallback:

1. Ensure your Supabase credentials are correct and Supabase is available
2. Make sure primary database connection string is set (MySQL or SQLite)
3. Call any API endpoint that performs database operations
4. To test fallback from Supabase to MySQL/SQLite, simulate Supabase unavailability:
   - Invalidate `SUPABASE_KEY` in environment
   - Or disconnect from network/block Supabase domain
5. Check the logs - you should see messages like:
   ```
   Attempting Supabase query for users
   Supabase query failed for users: ...
   Falling back to primary database for users
   Successfully created in primary database users
   ```

## Logging

The system provides detailed logging at each step:

- **INFO**: Successful primary database operations
- **WARNING**: Primary database failures and fallback attempts
- **ERROR**: Fallback failures or missing Supabase configuration
- **DEBUG**: Detailed query tracing

Enable debug logging to see all operations:

```python
import logging
logging.getLogger("database_fallback").setLevel(logging.DEBUG)
logging.getLogger("supabase_client").setLevel(logging.DEBUG)
```

## Important Notes

### Data Consistency

- The fallback is **asynchronous** - if Supabase (primary) recovers after using MySQL/SQLite fallback, existing MySQL/SQLite records won't automatically sync back
- For best results, ensure a working Supabase setup and have a sync strategy in place
- Consider adding a periodic sync job if using local database fallback long-term

### Type Conversion

- Supabase PostgreSQL types and SQLAlchemy models may have slightly different data types
- The helper functions return responses as-is from whichever database is used
- You may need to handle minor type differences (e.g., `datetime` objects as strings)

### Authentication

- Supabase uses Row-Level Security (RLS) policies
- The anon key should have appropriate RLS policies configured for your tables
- For production, configure RLS policies to restrict data access by user

## Troubleshooting

### Supabase connection fails

**Check:**
- `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Your Supabase project is active
- Check network connectivity to `api.supabase.co`
- Look for error messages in logs

### Tables not found in Supabase

**Solution:**
- Verify table names match exactly (case-sensitive)
- Run the SQL setup scripts provided above in Supabase SQL Editor
- Enable RLS policies if needed

### Data type mismatches

**Solution:**
- Ensure Supabase column types match SQLAlchemy model definitions
- Convert data types when converting between systems
- Use helper functions that handle type conversion

## Next Steps

1. Set up `.env` with your Supabase credentials
2. Create tables in Supabase using the SQL provided above
3. Update your routers to use the helper functions
4. Test fallback behavior by simulating primary database failure
5. Monitor logs during production usage

For more information about Supabase, visit: https://supabase.com/docs
