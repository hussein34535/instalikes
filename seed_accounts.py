import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv("dev.vars")

import api.python.database as db

accounts_data = [
    {"username": "elkozb@telegmail.com", "password": "haha77"},
    {"username": "feiyellivause-3318loy@yopmail.com", "password": "haha7#"},
    {"username": "tannacikicrou-7592kyr@yopmail.com", "password": "haha7#"},
    {"username": "louttetroimoma-8404ntrh@yopmail.com", "password": "haha7#"},
    {"username": "xeicreutassoba-2514df@yopmail.com", "password": "haha7#"},
    {"username": "frelijacraha-4919cbj@yopmail.com", "password": "haha7#"},
    {"username": "weijilovije-2126fhi@yopmail.com", "password": "haha7#"},
    {"username": "groupafefeitrei-8404dhj@yopmail.com", "password": "haha7#"},
    {"username": "quavedebeucri-9423khd@yopmail.com", "password": "haha7#"},
    {"username": "lafohogrede-2475iyc@yopmail.com", "password": "haha7#"},
    {"username": "yugunnaquoizu-3587floj@yopmail.com", "password": "haha7#"},
    {"username": "lattauppucico-2143kliu@yopmail.com", "password": "haha7#"},
    {"username": "quiprollebripu-1293lkf@yopmail.com", "password": "haha7#"},
    {"username": "magewuvatte-1342blk@yopmail.com", "password": "haha7#"},
    {"username": "roinnoubumebro-6151hgd@yopmail.com", "password": "haha7#"},
    # Duplicate removed implicitly by logic or DB constraint
    {"username": "rutregagrussa-6357lkj@yopmail.com", "password": "haha7#"},
    {"username": "kiqueiwautobro-5044kug@yopmail.com", "password": "haha7#"},
    {"username": "tamonafreli-1173csdg@yopmail.com", "password": "haha7#"},
    {"username": "gauttuttohoubri-7319jhg@yopmail.com", "password": "haha7#"},
    {"username": "sauhozissoquo-4430loug@yopmail.com", "password": "haha7#"},
    {"username": "jalevaxiti-5196luyg@yopmail.com", "password": "haha7#"},
    {"username": "trikaruzamma-2961liuv@yopmail.com", "password": "haha7#"},
    {"username": "xefruppoitreukei-7722liuh@yopmail.com", "password": "haha7#"},
    {"username": "grehaddossaunei-7257liy@yopmail.com", "password": "haha7#"},
    {"username": "sofrebraxaxu-1407mhv@yopmail.com", "password": "haha7#"},
    {"username": "xiyimoxege-8134liyg@yopmail.com", "password": "haha7#"},
    {"username": "labetinado-8373loih@yopmail.com", "password": "haha7#"},
    {"username": "prigeuzigezoi-1089liu@yopmail.com", "password": "haha7#"},
    {"username": "proiweleigrene-6971ngx@yopmail.com", "password": "haha7#"},
    {"username": "trougricoreila-9463dgh@yopmail.com", "password": "haha7#"},
    {"username": "bapoxenimmu-8819liuh@yopmail.com", "password": "haha7#"},
    {"username": "sallennakeussi-8413liyv@yopmail.com", "password": "haha7#"},
    {"username": "resazebrennou-9828kyrf@yopmail.com", "password": "haha7#"},
    {"username": "pegreuprauyoffe-4140ligb@yopmail.com", "password": "haha7#"},
    {"username": "pufoppeufraru-9210lijv@yopmail.com", "password": "haha7#"},
    {"username": "breffelloicrexa-4310lfs@yopmail.com", "password": "haha7#"},
    {"username": "kouleifallecroi-1692luh@yopmail.com", "password": "haha7#"},
    {"username": "woixoifappoute-8502lih@yopmail.com", "password": "haha7#"},
    {"username": "jebuvarayo-9190lkh@yopmail.com", "password": "haha7#"},
    {"username": "braffippoffaqueu-9560lhb@yopmail.com", "password": "haha7#"},
    {"username": "jeunnollussopre-8370igu@yopmail.com", "password": "haha7#"},
    {"username": "moubrajossauza-5757jfuh@yopmail.com", "password": "haha7#"},
    {"username": "crixeubreuceffeu-8811lfur@yopmail.com", "password": "haha7#"},
    {"username": "trehetripaffeu-3411kyt@yopmail.com", "password": "haha7#"},
    {"username": "bupiwelougrau-8656liyf@yopmail.com", "password": "haha7#"},
    {"username": "caroipaqueizo-4381hgd@yopmail.com", "password": "haha7#"},
    {"username": "bahoimmoukaufi-8100jhg@yopmail.com", "password": "haha7#"},
    {"username": "woxeyixillo-7342kyt@yopmail.com", "password": "haha7#"},
    {"username": "lauzameilibre-9969kyg@yopmail.com", "password": "haha7#"},
    {"username": "veihasufabu-6179hiyg@yopmail.com", "password": "haha7#"}
]

print(f"Importing {len(accounts_data)} accounts...")
stats = db.add_accounts_bulk(accounts_data)
print(f"Done! Added: {stats['added']}, Updated: {stats['updated']}")
