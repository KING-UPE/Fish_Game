import csv, json, sys, collections
p = sys.argv[1]; d = sys.argv[2]
rows = list(csv.reader(open(p, encoding='utf-8')))
hdr = rows[0]; rows = rows[1:]
assert hdr == ['id','name','category','phase','priority','hero','footprint','owner','status','score','notes'], hdr
bad = [r for r in rows if len(r) != 11]
print('rows', len(rows), 'badcols', len(bad), [r[0] for r in bad][:5])
ids = [r[0] for r in rows]
dup = [k for k,v in collections.Counter(ids).items() if v > 1]
print('dups', dup)
cats = {'Machine','Extractor','Power','Logistics','Structure','Special','Item','Tool','Vehicle','Creature','WreckKit','KitbashKit','EnvKit','Sky','FlashbackSet','Cinematic','UI'}
owners = {'asset-modeler','environment-artist','material-artist','vfx-artist','ui-artist','narrative-designer'}
for r in rows:
    if r[2] not in cats: print('badcat', r[0], r[2])
    if r[7] not in owners: print('badowner', r[0], r[7])
    if r[3] not in {'0','1','2','3','4','5','E'}: print('badphase', r[0], r[3])
    if r[4] not in {'P0','P1','P2'}: print('badprio', r[0])
    if r[5] not in {'y','n'}: print('badhero', r[0])
    if r[8] != 'planned' or r[9] != '': print('badstatus', r[0])
idset = {i.replace('_','') for i in ids} | set(ids)
b = json.load(open(d + '/buildables.json', encoding='utf-8'))
miss = [x['Name'] for x in b if x['Name'] not in idset]
print('buildables', len(b), 'missing', miss)
it = json.load(open(d + '/items.json', encoding='utf-8'))
mi = [x['Name'] for x in it if ('Item_' + x['Name']) not in ids and ('Tool_' + x['Name']) not in ids]
print('items', len(it), 'missing', mi)
# footprint check vs Size*8
byid = {r[0]: r for r in rows}
for x in b:
    rid = next((i for i in ids if i.replace('_','') == x['Name']), None)
    if rid is None: continue
    want = '%dx%d' % (round(x['Size']['X']*8), round(x['Size']['Y']*8))
    if not byid[rid][6].startswith(want): print('footprint', rid, byid[rid][6], 'want', want)
print('per category', dict(collections.Counter(r[2] for r in rows)))
print('per priority', dict(collections.Counter(r[4] for r in rows)))
print('hero y', sum(r[5]=='y' for r in rows))
print('per owner', dict(collections.Counter(r[7] for r in rows)))
print('per phase', dict(collections.Counter(r[3] for r in rows)))
