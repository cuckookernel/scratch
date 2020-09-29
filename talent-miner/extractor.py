from typing import Dict, Any, List, Optional
import yaml
import json
from json import JSONEncoder
import os
import re
import datetime as dt
import pandas as pd

from pprint import pprint
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import Tag
import numpy as np

HOME = Path( os.getenv('HOME') )

# TODO:
# Logros
# Destacado: cristian-david-montoya-saldarriaga-09638514a
# Herramientas y tecnologías

# TODO: features to extract
# Whether has resume available
# extract english level


# https://www.linkedin.com/in/luis-mario-urrea-murillo/
MY_PATH = HOME / '_data/talent'

SECS_IN_YEAR = 365.25 * 24 * 3600

COMMON_ENGLISH = {'the', 'with', 'on', 'and', 'I', 'am', 'is', 'my'}
COMMON_SPANISH = {'y', 'el', 'la', 'de', 'los', 'las'}


class _Config:
    raw_profiles_path = MY_PATH / 'linkedin_raw_profiles'
    profiles_yamls_path = MY_PATH / 'linkedin_yaml_profiles'


CFG = _Config


class DateTimeEncoder(JSONEncoder):
    """Override the default method"""
    def default(self, obj):
        """default formating as string"""
        if isinstance(obj, (dt.date, dt.datetime)):
            return obj.isoformat()

yaml.SafeDumper.yaml_representers[None] = lambda self, data: \
    yaml.representer.SafeRepresenter.represent_str( self, str(data) )
# %%


def main():
    """Read scraped profiles parse them and write to json and yamls"""
    # %%
    CFG.profiles_yamls_path.mkdir(parents=True, exist_ok=True)
    fpaths = list( _Config.raw_profiles_path.glob('*.html') )
    print( f'{len(fpaths)} htmls found' )
    # %%
    fpath = CFG.raw_profiles_path / 'luis-mario-urrea-murillo.html'
    # %%
    fpath = CFG.raw_profiles_path / 'cristian-david-montoya-saldarriaga-09638514a.html'
    # %%
    fpaths = [ CFG.raw_profiles_path / 'ricardo-alarcon-44079b105.html' ]
    # %%
    fpaths = [ Path('/home/teo/_data/talent/linkedin_raw_profiles/israellaguan.html')]
    # %%
    dics = {}
    # %%

    for i, fpath in enumerate(fpaths):
        if fpath in dics:
            continue

        with fpath.open('rt') as f_in:
            html = f_in.read()

        print( f'\n***{i+1}/{len(fpaths)} {fpath.name}:')
        dic = extract_one( html, fpath )
        dic['linkedin_url'] = f"https://www.linkedin.com/in/{fpath.name.split('.')[0]}"
        dic['scraped_at'] = dt.datetime.fromtimestamp( fpath.stat().st_ctime )
        # pprint(dic['work_stats'])
        dics[fpath] = dic

    dics_arr = list(dics.values())
    # %%
    del dics
    # %%

    with (CFG.profiles_yamls_path / 'all_profiles.json').open('wt') as f_out:
        json.dump( dics_arr, f_out, cls=DateTimeEncoder, indent=4 )
    # %%
    with (CFG.profiles_yamls_path / 'all_profiles.yaml').open('wt') as f_out:
        yaml.safe_dump( dics_arr, f_out )
    # %%
    df = produce_summary_table( dics_arr )
    df.to_excel( CFG.raw_profiles_path.parent / 'mined_ruby_candidates_sample.xlsx',
                 index=False)
    # %%


def _interactive_testing( dics_arr, fpaths, html: str ):
    # %%
    # noinspection PyUnresolvedReferences
    runfile('talent-miner/extractor.py')
    # %%
    pprint( dics_arr[4] )
    # %%
    fpath = [ f for f in fpaths if str(f).find('israellaguan') >= 0 ][0]
    # %%
    doc = BeautifulSoup( html, features='html.parser' )
    # %%
    _extract_accomplishments(doc)
    # %%


def _extract_accomplishments( doc: BeautifulSoup ) -> Dict[str, List[str]]:
    accomps = doc.find_all('section', {'class': 'pv-accomplishments-block'})

    # accomp0 = accomps[2]
    ret = {}
    for accomp in accomps:
        accomp_header = accomp.find_all('h3', {'class': 'pv-accomplishments-block__title'})[0].text
        accomp_vals = [ li_elem.text for li_elem in accomp.find_all('li') ]
        ret[accomp_header] = accomp_vals
    return ret
    # %%


def produce_summary_table( dics: List[Dict[str, Any]]) -> pd.DataFrame:
    # %%
    recs = []
    for dic in dics:
        try:
            w_stats = dic['work_stats']
            edu_stats = dic['education_stats']
            skills = dic['skills']
            rec = dict( name=dic['name'],
                        total_experience_yrs=w_stats['total_experience_yrs'],
                        n_work_positions=w_stats['n_work_positions'],
                        pos_lt1_year=w_stats['poss_lt1.2_years'],
                        pos_lt2_year=w_stats['poss_lt2_years'],
                        about=dic['about'],
                        about_eng_ratio=dic['about_stats']['about_eng_ratio'],
                        current_position=dic['current_position'],
                        has_worked_abroad=w_stats['has_worked_abroad'],
                        max_degree=edu_stats['max_degree'],
                        studied_abroad=edu_stats['has_studied_abroad'],
                        ruby=(skills.get('Ruby', -1) + 1) + (skills.get('Ruby on Rails', -1) + 1),
                        python=skills.get('Python (Programming Language)', -1) + 1,
                        java=skills.get('Java', -1) + 1,
                        javascript=skills.get('JavaScript', -1) + 1,
                        cpp=skills.get('C++', -1) + 1,
                        csharp=skills.get('C#', -1) + 1,
                        skills=skills,
                        profile_text_length=dic['profile_text_stats']['length'],
                        profile_eng_ratio=dic['profile_text_stats']['eng_ratio'] * 10.0,
                        languages=",".join ( dic.get('accomplishments', {}).get('idiomas', []) ),
                        num_contacts=dic['num_contacts'],
                        location=dic['location'],
                        linkedin_url=dic['linkedin_url'],
                        scraped_at=dic['scraped_at'])
        except Exception as exc:
            pprint( dic )
            raise exc
        recs.append(rec)

    df = pd.DataFrame( recs )
    # %%
    return df
    # %%


def extract_one( html: str, fpath: Path ):
    """Extract data from one scraped html"""
    # %%
    doc = BeautifulSoup( html, features='html.parser')

    ret = { 'linkedin_handle': fpath.name.split('.')[0] }
    _parse_top_card( ret, doc )
    # %%
    ret['about'] = _extract_about( doc )
    # if len(ret['about']) < 100 and ret['about'].find('ver más') > 0:
    #    print( f"\nVer más detected: \nabout:{ret['about']} fpath={fpath}" )

    ret['about_stats'] = {'about_eng_ratio': _common_english_ratio(ret['about'])}
    # %%
    ret['work_experience'] = _parse_experiences( doc )
    ret['work_stats'] = calc_work_stats( ret['work_experience'])
    # %%
    ret['skills'] = proc_skills_section( doc )
    ret['education'] = _parse_education( doc )
    ret['education_stats'] = _education_stats( ret['education'])
    ret['accomplishments'] = _extract_accomplishments(doc)
    ret['profile_text_stats'] = profile_text_stats( doc )
    # %%
    return ret
    # %%


def calc_work_stats( work_xps: List[Dict[str, Any]] ):
    """Calculate total_experience_yrs and other stats"""
    durations = [ rec['duration'] for rec in work_xps if 'duration' in rec ]
    total_years = sum( durations ) if durations else None
    avg_years = np.round( total_years / len(durations), 2) if durations else None
    poss_lt2_years = sum( 1 for dur in durations if dur < 2.0 )
    poss_lt1_2_years = sum(1 for dur in durations if dur < 1.2 )

    has_worked_abroad = any( rec for rec in work_xps
                             if _is_location_abroad( rec.get('location_raw') ))

    return { "total_experience_yrs": total_years,
             'avg_years': avg_years,
             'n_work_positions': len(durations),
             'poss_lt2_years': poss_lt2_years,
             'poss_lt1.2_years': poss_lt1_2_years,
             'has_worked_abroad': has_worked_abroad }
    # %%


def _is_location_abroad( location: Optional[str] ):
    if location is None or location.strip() == '':
        return False
    else:
        ret = not re.search( 'Colombia|Medell.n|Bogot.|Barranquilla|Cali|Pereira'
                             '|Caldas|Cucuta|Dosquebradas|Antioquia|Remot[eo]',
                             location, re.IGNORECASE)
        if ret:
            print( f'abroad location: {location}')
        return ret


def _is_abroad_school( school: Optional[str] ):
    ret = re.search(r"(University|College|\bof\b)", school)

    if ret:
        print( f'abroad school: {school}')

    return ret


def profile_text_stats( doc: BeautifulSoup ):
    """some metrics on the whole profile text"""
    text = doc.find('main', {'class': 'core-rail'}).text.strip()
    words = text.split()
    eng_ratio = sum(1 for word in words if word in COMMON_ENGLISH) * 10/ (len(words) + 0.001)
    return { 'length': len( text ),
             'eng_ratio': np.round( eng_ratio, 2)}
    # %%


def _extract_about( doc ) -> Optional[str]:

    about_section = doc.find('section', {'class': 'pv-about-section'})
    if about_section is None:
        return None

    parts = about_section.find_all("p")
    return (" ".join( part.text.replace('\n', ' ').strip() for part in parts )
            .replace( '... ver más', '') )
    # %%


def _parse_top_card( ret: Dict[ str, Any], doc: BeautifulSoup ):
    top_card_els = doc.find_all( "ul", {"class": "pv-top-card--list"} )
    name_elem = top_card_els[0].find_all("li")[0]
    name = name_elem.text.strip()

    current_position = doc.find_all("h2", {"class": "mt1"})[0].text.strip()
    location = top_card_els[1].find_all( "li" )[0].text.strip()
    # %%
    num_contacts = _extract_num_contacts(  top_card_els[1] )
    # %%
    top_card_xp = doc.find_all('a', {"class": "pv-top-card--experience-list-item"})
    main_school = top_card_xp[0].text.strip() if top_card_xp else None

    data = dict(name=name,
                current_position=current_position,
                location=location,
                num_contacts=num_contacts,
                main_school=main_school)

    ret.update(data)
    # %%


def _extract_num_contacts( elem: Tag ):
    num_contacts_text = elem.find_all("li")[1].text.strip()
    mch = re.match(r'(\d+) contactos', num_contacts_text)
    if mch:
        return int(mch.group(1))
    mch2 = re.search(r'Más de 500 contactos', num_contacts_text)
    if mch2:
        return 501


def _parse_experiences(doc: BeautifulSoup) -> List[Dict]:
    # %%
    xp_section = doc.find( 'section', {'id': 'experience-section'} )
    if xp_section is None:
        return []
    # %%
    summaries = xp_section.find_all('div', {'class': 'pv-entity__summary-info'})
    ret = [ proc_employment_summary(summary) for summary in summaries ]

    return ret
    # %%


def proc_employment_summary(summary: Tag) -> Dict:
    """process one employment summary and extract info from it"""

    xp_record = dict()
    xp_record['position'] = summary.find('h3').text.strip()
    company = summary.find_all('p', {'class': 'pv-entity__secondary-title'})[0]
    xp_record['company'] = "; ".join( [ line.strip() for line in company.text.split('\n')
                                        if line.strip() != ''] )
    # %%
    for xp_line in summary.find_all('h4'):
        fld_name, value = [span.text.strip() for span in xp_line.find_all('span') ]
        if fld_name == 'Fechas de empleo':
            xp_record['period_raw'] = value
            period = _extract_period( value )
            xp_record['period'] = period
            # print( period )
            xp_record['duration'] = np.round( (period[1] - period[0]).total_seconds()
                                              / SECS_IN_YEAR, 2)
        elif fld_name == 'Duración del empleo':
            xp_record['duration_raw'] = value
        elif fld_name == 'Ubicación':
            xp_record['location_raw'] = value
            # print( f'location: {value}')
        elif fld_name.startswith('LinkedIn me ayud'):
            continue
        else:
            print( "proc_employment_summary: ",  fld_name, value )
    # %%
    # pprint( xp_record )
    # %%
    return xp_record
    # %%


def _extract_period( period_raw: str ):
    mch2 = re.match(r'(?P<mes1>[a-z]+)\. de (?P<year1>[0-9]+) . '
                    r'(?P<mes2>[a-z]+)\. de (?P<year2>[0-9]+)', period_raw)
    if mch2:
        # print('mch2', mch2, mch2.group("year1"), mch2.group("year2"))
        mes1, mes2 = _translate_mes(mch2.group("mes1")), _translate_mes(mch2.group("mes2"))
        return ( dt.date(int(mch2.group("year1")), int( mes1 ), 1),
                 dt.date(int(mch2.group("year2")), int( mes2 ), 1) )

    mch1 = re.match(r'(?P<mes>[a-z]+)\. de (?P<year>[0-9]+)( . actualidad)?', period_raw)
    if mch1:
        # print('mch1')
        mes = _translate_mes(mch1.group("mes"))
        return dt.date(int(mch1.group("year")), mes, 1), dt.date.today()

    mch2b = re.match(r'(?P<mes1>[a-z]+)\. de (?P<year1>[0-9]+) . (?P<year2>[0-9]{4})', period_raw)
    if mch2b:
        mes1 = _translate_mes(mch2b.group("mes1"))
        return ( dt.date(int(mch2b.group("year1")), int(mes1), 1),
                 dt.date(int(mch2b.group("year2")), 1, 1) )

    mch3 = re.match(r'(?P<year1>[0-9]{4}) . (?P<year2>[0-9]{4})', period_raw)
    if mch3:
        return (dt.date(int(mch3.group("year1")), 1, 1),
                dt.date(int(mch3.group("year2")), 1, 1))

    mch4 = re.match(r'(?P<year1>[0-9]{4})', period_raw)
    if mch4:
        return (dt.date(int(mch4.group("year1")), 1, 1),
                dt.date(int(mch4.group("year1")) + 1, 1, 1))

    assert False, period_raw
    # %%


def _interactive_test():
    # %%
    period_raw = 'ene. de 2015 – actualidad'
    # %%
    period_raw = 'ene. de 2015 – may. de 2015'
    print( _extract_period( period_raw ) )
    # %%
    period_raw = 'ene. de 2012 – may. de 2013'
    print(_extract_period(period_raw))

    # %%


def _translate_mes( mes: str) -> int:
    return {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dic': 12}[mes]


def _common_english_ratio( a_text: str ) -> int:
    if a_text is None:
        return None

    words = a_text.split()
    cnt_english = sum( 1 for word in words if word in COMMON_ENGLISH )

    return np.round( cnt_english / (len(words) + 0.001) * 10, 2)


def _parse_education(doc: BeautifulSoup) -> List[Dict]:
    # %%
    edu_section = doc.find( 'section', {'id': 'education-section'} )
    # %%
    if edu_section is None:
        return []
    # %%
    summaries = edu_section.find_all('li', {'class': 'pv-education-entity'})

    ret = [ proc_education_summary(summary) for summary in summaries ]
    # %%
    return ret
    # %%


def _education_stats( edu_records: List[Dict[str, str]]):
    return {'has_studied_abroad': any(rec['is_abroad_school'] for rec in edu_records),
            'max_degree': _max_degree(edu_records)}


def proc_education_summary( summary: Tag ) -> Dict[str, str]:
    """Process one education summary and generate a record"""
    edu_record = dict()
    edu_record['school'] = summary.find('h3').text.strip()
    edu_record['is_abroad_school'] = _is_abroad_school( edu_record['school'] )

    for parag in summary.find_all('p'):
        spans = [span.text.strip() for span in parag.find_all('span')]
        if len( spans ) == 2:
            fld_name, value = spans
            value = value.strip()
        elif len(spans) == 0:
            # print( 'education parag: ', parag )
            edu_record['description'] = parag.text.strip()
            continue
        else:
            print( 'education spans: ', spans )
            continue

        if fld_name == 'Nombre de la titulación':
            edu_record['degree_raw'] = value
            edu_record['degree'] = _classify_degree( value )
            # print( 'degree: ', value, _classify_degree(value) )
        elif fld_name == 'Disciplina académica':
            edu_record['field_raw'] = value
        elif fld_name == 'Nota':
            edu_record['grade_raw'] = value
        elif fld_name.startswith('Fechas de estudios'):
            edu_record['period_raw'] = value
        elif fld_name.startswith('Actividades y asociaciones'):
            edu_record['activities_raw'] = value
        else:
            print("proc_education_summary: ", fld_name, '  :: ', value)

    if edu_record.get('degree', 'Unknown') == 'Unknown':
        if re.search( 'Ingenier|Engineering', edu_record.get('field_raw', '') ):
            edu_record['degree'] = 'University'

    return edu_record
    # %%


def _classify_degree( degree: str ) -> str:
    if re.search('Ingenier|Engineer', degree):
        return 'University'
    elif re.search('^Tecn.log', degree):
        return 'Tecnología'
    elif re.search('^Mae?ste?r', degree):
        return 'Master''s'
    elif re.search('^Dimplom', degree):
        return 'Diploma'
    elif re.search('^(Esp\.|Especializ)', degree):
        return 'Specialization'
    elif re.search('^Phd', degree, re.IGNORECASE):
        return 'PhD'
    else:
        return 'Unknown'


DEGREE_LEVELS = {'Tecnología': 1, 'University': 2, 'Diploma': 3,
                 'Specialization': 4, 'Master''s': 5, 'PhD': 5, 'Unknown': -1}


def _max_degree(edu_records: List[Dict[str, str]]) -> Optional[str] :
    levels = DEGREE_LEVELS

    if len(edu_records) > 0:
        return max( [rec.get('degree', 'Unknown') for rec in edu_records ],
                    key=lambda x: levels[x])
    else:
        return None


def proc_skills_section( doc: BeautifulSoup ):
    # %%
    skills_section = doc.find('section', {'class': 'pv-skill-categories-section'})
    if skills_section is None:
        return {}
    # %%
    divs = skills_section.find_all('div', {'class': 'pv-skill-category-entity__skill-wrapper'})
    # %%
    ret = {}
    for div in divs:
        texts = [ span.text.strip() for span in div.find_all('span') if span.text.strip() != '' ]
        if len(texts) >= 1:
            key = texts[0]

            if len(texts) >= 3:
                mch = re.match(r'(\d+)', texts[2])
                if mch:
                    ret[key] = int( mch.group(1))

                else:
                    print( f"skills {len(texts)} spans: {texts}")
                    ret[key] = None
            elif len(texts) == 1:
                ret[key] = 0
            else:
                print(f"skills {len(texts)} spans: {texts}")

    # %%
    return ret