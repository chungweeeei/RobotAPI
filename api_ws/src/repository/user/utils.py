from sqlalchemy import DDL

"""
    {TODO} information for using sqlalchemy DDL instance
"""

delete_user_func = DDL(
   "CREATE OR REPLACE FUNCTION record_user_delete() "
   "RETURNS TRIGGER AS $$ "
   "BEGIN "
   "INSERT INTO user_info_deleted "
   "VALUES (OLD.user_id, OLD.user_name, OLD.user_role, NOW()); "
   "RETURN OLD; "
   "END; $$ LANGUAGE PLPGSQL"
)

delete_user_trigger = DDL(
    "CREATE TRIGGER check_user_delete "
    "AFTER DELETE ON user_info "
    "FOR EACH ROW "
    "EXECUTE FUNCTION record_user_delete();"
)

