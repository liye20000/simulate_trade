for file in *.zip; do
    unzip -o "$file"
done
awk 'NR == 1 || FNR > 1' *.csv > merged.csv