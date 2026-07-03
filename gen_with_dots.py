import geopandas as gpd
from shapely.geometry import MultiPolygon, Point
import json
from region_coords import REGION_LATLON

w50 = gpd.read_file('ne50.geojson')
NAME='NAME'

def _span_tol(polys, frac):
    xs=[];ys=[]
    for p in polys:
        x0,y0,x1,y1=p.bounds; xs+=[x0,x1]; ys+=[y0,y1]
    span=max(max(xs)-min(xs), max(ys)-min(ys)) or 1
    return span*frac

# origin key -> (Natural Earth name, extraction params)
MAINLAND={
 'brazil':'Brazil','colombia':'Colombia','ethiopia':'Ethiopia','kenya':'Kenya','vietnam':'Vietnam',
 'india':'India','mexico':'Mexico','peru':'Peru','png':'Papua New Guinea','guatemala':'Guatemala',
 'costarica':'Costa Rica','honduras':'Honduras','nicaragua':'Nicaragua','elsalvador':'El Salvador',
 'yemen':'Yemen','tanzania':'Tanzania','rwanda':'Rwanda','ecuador':'Ecuador','bolivia':'Bolivia',
 'uganda':'Uganda','malawi':'Malawi','zambia':'Zambia','zimbabwe':'Zimbabwe','burundi':'Burundi',
 'thailand':'Thailand','china':'China','timor':'Timor-Leste','jamaica':'Jamaica','panama':'Panama',
 'congo':'Dem. Rep. Congo',
}
SILKEY={  # origin key -> the COUNTRY_SIL key used in build.py
 'brazil':'Brazil','colombia':'Colombia','ethiopia':'Ethiopia','kenya':'Kenya','vietnam':'Vietnam',
 'india':'India','mexico':'Mexico','peru':'Peru','png':'Papua New Guinea','guatemala':'Guatemala',
 'costarica':'Costa Rica','honduras':'Honduras','nicaragua':'Nicaragua','elsalvador':'El Salvador',
 'yemen':'Yemen','tanzania':'Tanzania','rwanda':'Rwanda','ecuador':'Ecuador','bolivia':'Bolivia',
 'uganda':'Uganda','malawi':'Malawi','zambia':'Zambia','zimbabwe':'Zimbabwe','burundi':'Burundi',
 'thailand':'Thailand','china':'China (Yunnan)','timor':'Timor-Leste','jamaica':'Jamaica','panama':'Panama',
 'congo':'DR Congo','sumatra':'Indonesia (Sumatra)','java':'Java','sulawesi':'Sulawesi (Toraja)',
 'bali':'Bali (Kintamani)','flores':'Flores (Bajawa)','hawaii':'Hawaii (Kona)',
}

def polys_for(origin):
    """Return the polygons used for a given origin's silhouette + the extraction, matching gen_silhouettes."""
    small={'nicaragua','elsalvador','rwanda','burundi','timor','jamaica','costarica','panama','guatemala','honduras'}
    if origin in MAINLAND:
        ne=MAINLAND[origin]
        geom=w50[w50[NAME]==ne].geometry.values[0]
        polys=sorted(geom.geoms,key=lambda p:p.area,reverse=True) if isinstance(geom,MultiPolygon) else [geom]
        af=0.12
        if origin in ('ecuador','yemen','india','tanzania','png'): af=0.20
        main=polys[0].area; polys=[p for p in polys if p.area>main*af]
        tol=_span_tol(polys, 0.006)
        polys=[p.simplify(tol,preserve_topology=True) for p in polys]
        return polys
    # islands
    ISL={'sumatra':('Indonesia',101.6,-0.4,0.004),'java':('Indonesia',110.2,-7.3,0.004),
         'sulawesi':('Indonesia',121.2,-2.1,0.004),'flores':('Indonesia',121.3,-8.6,0.004),
         'bali':('Indonesia',115.1,-8.3,0.003)}
    if origin in ISL:
        ctry,cx,cy,frac=ISL[origin]
        geom=w50[w50[NAME]==ctry].geometry.values[0]
        polys=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
        best=min(polys,key=lambda p:p.centroid.distance(Point(cx,cy)))
        tol=_span_tol([best], frac)
        return [best.simplify(tol,preserve_topology=True)]
    if origin=='hawaii':
        geom=w50[w50[NAME]=='United States of America'].geometry.values[0]
        polys=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
        centers=[(-155.5,19.6),(-156.3,20.8),(-157.0,21.3),(-158.0,21.5),(-159.5,22.0)]
        chosen=[]
        for (cx,cy) in centers:
            p=min(polys,key=lambda q:q.centroid.distance(Point(cx,cy)))
            if p not in chosen: chosen.append(p)
        tol=_span_tol(chosen, 0.004)
        return [p.simplify(tol,preserve_topology=True) for p in chosen]
    return None

def transform_fn(polys):
    """Same normalization as gen_silhouettes: centered in 0..100, Y flipped."""
    allc=[]
    for p in polys: allc+=list(p.exterior.coords)
    xs=[c[0] for c in allc]; ys=[c[1] for c in allc]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    span=max(maxx-minx,maxy-miny) or 1
    offx=(100-(maxx-minx)/span*100)/2
    offy=(100-(maxy-miny)/span*100)/2
    def tx(lon,lat):
        return (offx+(lon-minx)/span*100, offy+(maxy-lat)/span*100)
    return tx,(minx,maxx,miny,maxy)

# generate region dots for each origin
region_dots={}
for origin in SILKEY:
    polys=polys_for(origin)
    if not polys: continue
    tx,bounds=transform_fn(polys)
    latlon=REGION_LATLON.get(origin,{})
    dots=[]
    for name,coord in latlon.items():
        if coord is None:
            dots.append(None)  # keep index alignment with regions2, but no dot
        else:
            lon,lat=coord
            x,y=tx(lon,lat)
            dots.append([round(x,1),round(y,1)])
    region_dots[SILKEY[origin]]=dots
json.dump(region_dots,open('region_dots.json','w'))
# report: how many dots fall INSIDE the shape bbox 0..100 (sanity)
oob=0;tot=0
for k,dots in region_dots.items():
    for dxy in dots:
        if dxy:
            tot+=1
            if not(0<=dxy[0]<=100 and 0<=dxy[1]<=100): oob+=1
print(f'{len(region_dots)} origins, {tot} dots placed, {oob} outside 0..100 box')
