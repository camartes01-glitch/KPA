CONF=$(find /etc/postgresql/ -name postgresql.conf)
HBA=$(find /etc/postgresql/ -name pg_hba.conf)

echo "listen_addresses = '*'" >> "$CONF"
echo "host all all 0.0.0.0/0 md5" >> "$HBA"
echo "host all all 0.0.0.0/0 scram-sha-256" >> "$HBA"
echo "host all all all trust" >> "$HBA"

/usr/sbin/service postgresql restart
