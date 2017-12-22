from postgres_bkp import Pg_Backup

BKP_CONFIG = {
    'server_name': 'rancher-apps-homolog',
    'db_name_record': 'core_backup',
    'total_steps': 3.0,
    'db_name_log_record': 'core_backuplog',
    'user_password': 'g3n0m1k@',
    'pg_user': 'genomika',
    'host_machine': '172.16.225.18',
    'db_password': 'g3n3t1c@',
    'port': '5432',
    'local_destiny_folder': '/rancher/shannon/',
    'server_mount_folder': '/shannon/genomikalab/Backups/Bancos/',
    'DB_IGNORED': [
        'template1',
        'template0',
        'postgres'
    ],
    # 'server_user': 'genomika',
    # 'server_address': '172.16.225.15',
    # 'server_password': 'g3n3t1c@',
    'days_delete': 7,
    'folders_to_pass': [
    ],
    'send_email_success': True
}

EMAIL_CONFIG = {
    'recipient_list': ['joao.victor@genomika.com.br', 'suporte@genomika.com.br'],
    'email_host': 'notificacoes@genomika.com.br',
    'email_password': 'g3n0m1k@',
    'host': 'smtp.gmail.com',
    'domain': 'gmail.com',
    'port': '465',
    'local_password': BKP_CONFIG['user_password']
}

bkp = Pg_Backup(BKP_CONFIG, EMAIL_CONFIG)
bkp.backup()
