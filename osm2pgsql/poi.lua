local pois = osm2pgsql.define_table({
    name = 'pois',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name' },
        { column = 'class', not_null = true },
        { column = 'subclass' },
        { column = 'geom', type = 'point', not_null = true, projection = 4326 },
        { column = 'version', type = 'smallint' },
        { column = 'age', type = 'real'},
}})

function age(ts)
    return os.difftime(os.time(), ts) / ( 60 * 60 * 24 )
end

function process_poi(object, geom)

    function age(ts)
        return os.difftime(os.time(), ts) / ( 60 * 60 * 24 )
    end

    local a = {
        name = object.tags.name,
        version = object.version,
        age = age(object.timestamp),
        geom = geom
    }

    if object.tags.amenity then
        a.class = 'amenity'
        a.subclass = object.tags.amenity
    elseif object.tags.shop then
        a.class = 'shop'
        a.subclass = object.tags.shop
    elseif object.tags.tourism then
        a.class = 'tourism'
        a.subclass = object.tags.tourism
    elseif object.tags.craft then
        a.class = 'craft'
        a.subclass = object.tags.craft
    elseif object.tags.emergency then
        a.class = 'emergency'
        a.subclass = object.tags.emergency
    elseif object.tags.leisure then
        a.class = 'leisure'
        a.subclass = object.tags.leisure
    elseif object.tags.office then
        a.class = 'office'
        a.subclass = object.tags.office
    elseif object.tags.sport then
        a.class = 'sport'
        a.subclass = object.tags.sport
    else
        return
    end

    pois:insert(a)
end

function osm2pgsql.process_node(object)
    process_poi(object, object:as_point())
end

function osm2pgsql.process_way(object)
    if object.is_closed and object.tags.building then
        process_poi(object, object:as_polygon():centroid())
    end
end