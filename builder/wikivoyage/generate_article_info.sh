#!/bin/bash

set -e -u -x

# Do not create article_info.txt now so that if we fail make will not consider the job done.
rm article_info.tmp || true

for REGION in United_Kingdom Ireland Italy Switzerland Liechtenstein Belarus Spain Portugal France Germany
do
    # Create an empty table.
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="DROP TABLE IF EXISTS $REGION"
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="CREATE TABLE $REGION \
        (id int(10) unsigned, gen int(3), id1 int(10), title1 varbinary(255), id2 int(10), title2 varbinary(255), primary key(id))"

    # Insert the seed category.
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="INSERT INTO $REGION(id, gen) \
        SELECT page_id, 0 FROM page WHERE page_title = '$REGION';"

    # In a loop insert all children (both pages and categories).
    for i in `seq 1 10`
    do
        $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="INSERT INTO $REGION(id, gen, id1, title1) \
            SELECT cl_from, $i, page_id, page_title \
            FROM categorylinks \
            JOIN page ON cl_to = page_title \
            JOIN $REGION ON page_id = id \
            WHERE cl_from NOT IN (SELECT id from $REGION) GROUP BY cl_from"
    done

    # Update id1 (id of parent).
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="UPDATE $REGION r1 \
        JOIN page ON r1.title1 = page_title AND page_namespace = 0 \
        JOIN $REGION r2 ON page_id = r2.id \
        SET r1.id1 = r2.id"

    # Update id2 and title2 (for grandparents).
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="UPDATE $REGION r1 \
        JOIN $REGION r2 ON r1.id1 = r2.id \
        SET r1.id2 = r2.id1, r1.title2 = r2.title1"

    # Output the final result.
    $MYSQL_BINARY --user=$MYSQL_USER --database=$MYSQL_DATABASE --execute="SELECT \
        page_id, page_title, page_len, image.pp_value, id1, title1, id2, title2 \
        FROM $REGION \
        JOIN page ON page_id = id \
        LEFT JOIN page_props image ON image.pp_page = id and image.pp_propname = 'page_image' \
        WHERE page_namespace = 0 \
        ORDER BY page_title" \
        --skip-column-names > $REGION.info.txt

    echo $REGION >> countries.tmp
done

# Now we are done. Create the final file.
mv countries.tmp countries.txt