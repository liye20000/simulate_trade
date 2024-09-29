echo "Hello , Let's start!"
./clean_up.sh
./download-futures-klines-simultaneously.sh
./unzip_and_merge.sh
cp merged.csv ../../../BTCUSDT-2024-to-8-1h.csv
./clean_up.sh