try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Bypass Django's MariaDB >= 10.6 check so XAMPP MariaDB 10.4 works seamlessly
setattr(BaseDatabaseWrapper, "check_database_version_supported", lambda self: None)

# MariaDB < 10.5 does not support the 'RETURNING' clause in INSERT statements
def _can_return_columns_from_insert(self):
    return bool(self.connection.mysql_is_mariadb and self.connection.mysql_version >= (10, 5))

setattr(DatabaseFeatures, "can_return_columns_from_insert", property(_can_return_columns_from_insert))
setattr(DatabaseFeatures, "can_return_rows_from_bulk_insert", property(_can_return_columns_from_insert))


