local pois = osm2pgsql.define_table({
    name = 'pois',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name' },
        { column = 'class', not_null = true },
        { column = 'subclass', not_null = true },
        { column = 'geom', type = 'point', not_null = true, projection = 4326 },
        { column = 'version', type = 'smallint', not_null = true },
        { column = 'timestamp', sql_type = 'timestamp', not_null = true},
}})

function format_date(ts)
    --- borrowed from https://github.com/openstreetmap/osm2pgsql/blob/ad541d2a536a63de162d6266a6670aa2172b2749/flex-config/attributes.lua#L52
    return os.date('!%Y-%m-%dT%H:%M:%SZ', ts)
end

function process_poi(object)
    local fields = {
        name = object.tags.name,
        version = object.version,
        timestamp = format_date(object.timestamp),
    }

    if object.tags.amenity then
        fields.class = 'amenity'
        fields.subclass = object.tags.amenity
    elseif object.tags.shop then
        fields.class = 'shop'
        fields.subclass = object.tags.shop
    else
        return {}
    end
    return fields
end

function osm2pgsql.process_node(object)
    record = process_poi(object)
    if record.class then 
        record.geom = object:as_point()
        pois:insert(record)
    end
end

function osm2pgsql.process_way(object)
    if object.is_closed and object.tags.building then
        record = process_poi(object)
        if record.class then
            record.geom = object:as_polygon():centroid()
            pois:insert(record)
        end
    end
end