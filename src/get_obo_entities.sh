# from https://github.com/lubianat/obo_to_mixnmatch/blob/main/src/get_all_entities.sh

wget -nc -O data/$1.owl  http://purl.obolibrary.org/obo/$1.owl


robot export --input data/$1.owl \
  --header "ID|LABEL|IAO_0000115|hasDbXref|subClassOf [ID]" \
  --export data/$1.csv

grep -v "obsolete" data/$1.csv | grep -v ",,"| grep -i ^$1:  > data/$1_clean.csv

sed -i '1s/^/id,name,description,xrefs,parents\n /' data/$1_clean.csv

upperstr=$(echo $1 | tr '[:lower:]' '[:upper:]')

if [[ $2 != "--no-change" ]]
then
  if [[ $2 == "--underscore" ]]
  then
    sed -i "s/:/_/" data/$1_clean.csv

  else
    sed -i "s/$upperstr://" data/$1_clean.csv
  fi
else
    echo "No change"
fi