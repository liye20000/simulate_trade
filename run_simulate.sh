echo '开始后台运行模拟程序'
nohup  /home/ubuntu/anaconda3/bin/python3.11 /home/ubuntu/simulate_trade/bt_run_data.py > /home/ubuntu/simulate_trade/debug/backround_log.log 2>&1 &