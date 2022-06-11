#Alvaro alonso

read -p "Indique los minutos: " minutos

seg=$((minutos * 60 + 1))

while [ $seg != 0 ]; do
       let seg=($seg-1)
       echo "Quedan $seg segundos"
       sleep 1
done