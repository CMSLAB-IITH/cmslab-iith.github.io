"""Build the static CμMS website. Edit data/group.json, then run python3 build.py."""
from pathlib import Path
import html
import json
root=Path(__file__).resolve().parent
data=json.loads((root/'data/group.json').read_text())
escape=html.escape

def link(url,label):
    return f'<a href="{escape(url,quote=True)}">{escape(label)} ↗</a>'

def person_card(person,collaborator=False):
    image=person.get('image')
    portrait=f'<img src="{escape(image.lstrip("/"))}" alt="{escape(person["name"])}" width="64" height="72" loading="lazy">' if image else f'<span class="initials" aria-hidden="true">{escape(person["initials"])}</span>'
    body=f'<h3>{escape(person["name"])}</h3><p class="affiliation">{escape(person.get("note",""))}</p>'
    if person.get('research'): body+=f'<p>{escape(person["research"])}</p>'
    if person.get('works'):
        body+='<ul class="works">'+''.join(f'<li><small>{escape(work["kind"])}</small>{link(work["url"],work["title"])}</li>' for work in person['works'])+'</ul>'
    links=[]
    if collaborator:
        if person.get('homepage'): links.append(link(person['homepage'],'Homepage'))
        links.extend([link(person['institute_profile'],'Institute profile'),link(person['institute_url'],'Institute')])
    else:
        if person.get('url'): links.append(link(person['url'],person.get('link_label','Research profile')))
        if person.get('linkedin'): links.append(link(person['linkedin'],'LinkedIn'))
    body+='<div class="profile-links">'+''.join(links)+'</div>'
    return f'<article class="person">{portrait}<div>{body}</div></article>'

def page(filename,title,content):
    nav=''.join(f'<a href="{url}"'+(' aria-current="page"' if filename==url else '')+f'>{label}</a>' for url,label in [('index.html','Home'),('people.html','People'),('research.html','Research'),('collaborators.html','Collaborators'),('group-life.html','Group life')])
    document=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} · CμMS · IIT Hyderabad</title><meta name="description" content="Computational Microstructure Modeling and Simulation at IIT Hyderabad: phase-field modeling, elasticity, diffusion and physics-informed learning."><link rel="canonical" href="https://cmslab-iith.github.io/{'' if filename=='index.html' else filename}"><link rel="stylesheet" href="assets/site.css"><link rel="icon" href="assets/mark.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Libre+Caslon+Display&display=swap" rel="stylesheet"></head><body><a class="skip" href="#main">Skip to content</a><header><a class="identity" href="index.html"><span class="mark" aria-label="C mu M S">C<span>μ</span>MS</span><span>Computational Microstructure<br>Modeling and Simulation<small>PART OF M³ LAB · IIT HYDERABAD</small></span></a><nav aria-label="Main navigation">{nav}<a href="https://saswataiith.github.io/">Saswata’s website ↗</a></nav></header><main id="main">{content}</main><footer><div><span class="eyebrow">CμMS · IIT HYDERABAD</span><h2>Understanding how<br>microstructures evolve.</h2><p>Materials Science and Metallurgical Engineering<br>Indian Institute of Technology Hyderabad</p><div class="profile-links">{link('https://saswataiith.github.io/','Prof. Saswata Bhattacharya')}{link('https://github.com/CMSLAB-IITH/cmslab-iith.github.io','Website source')}{link('https://github.com/CMSLAB-IITH/cmslab-iith.github.io/blob/main/CONTRIBUTING.md','Member editing guide')}</div></div><a href="https://iith.ac.in/"><img class="institute-logo" src="assets/images/iith-logo.png" alt="IIT Hyderabad" width="240"></a></footer></body></html>'''
    (root/filename).write_text(document)

def heading(kicker,title,description):
    return f'<section class="heading"><span class="eyebrow">{kicker}</span><h1>{title}</h1><p>{description}</p></section>'

lab_context='<section class="tinted lab-context"><span class="eyebrow">OUR SHARED LABORATORY</span><h2>M³ Lab · Multiscale Modeling of Materials</h2><p>M³ Lab at IIT Hyderabad is jointly led by <a href="https://saswataiith.github.io/">Prof. Saswata Bhattacharya</a> and <a href="https://iith.ac.in/msme/anujgoyal/">Prof. Anuj Goyal</a>.</p><p>Within M³ Lab, the <strong>CμMS Group (Computational Microstructure Modeling and Simulation)</strong> is led by Prof. Saswata Bhattacharya. This website presents the work, people and activities of the CμMS Group.</p></section>'

research='''<div class="topics"><article><span class="number">01</span><h3>Elastic stress effects</h3><p>How eigenstrain, elastic anisotropy and elastic inhomogeneity select precipitate shapes and orientations.</p><a href="https://saswataiith.github.io/research/elastic-lab/">Explore the elastic stress laboratory →</a></article><article><span class="number">02</span><h3>Phase-field microstructures</h3><p>Phase separation, superalloy precipitates, bimetallic nanoparticles and ferroelectric domains, connected through thermodynamics and kinetics.</p><a href="https://saswataiith.github.io/research/">Research and formulations →</a></article><article><span class="number">03</span><h3>Physics-informed learning</h3><p>Inverse diffusion problems, multiobjective optimization and surrogate models that connect observations to governing equations.</p><a href="https://saswataiith.github.io/resources/pinns/">Learn the PINN idea →</a></article></div>'''
page('index.html','Computational Microstructure Modeling and Simulation',heading('COMPUTATIONAL MICROSTRUCTURE MODELING AND SIMULATION','Small structures.<br><em>Rich physical ideas.</em>','We study how thermodynamics, transport and mechanics shape materials. Led by Prof. Saswata Bhattacharya at IIT Hyderabad, our group develops computational models that make the underlying physics visible.')+lab_context+f'<section><h2>From physical mechanisms to materials design.</h2>{research}</section><section class="tinted"><h2>Science grows through people.</h2><p>Meet our current members, former members and collaborators across institutions.</p><div class="profile-links"><a href="people.html">Group members →</a><a href="collaborators.html">Collaborators →</a></div></section>')
people=heading('OUR GROUP','People &amp; <em>their work.</em>','Current members, former members and jointly supervised researchers. Explore their research and selected publications.')
people+=lab_context
people+='<section class="pi"><h2>Group lead</h2><article class="person"><img src="assets/images/group/prof-saswata-bhattacharya.jpg" alt="Prof. Saswata Bhattacharya" width="64" height="72"><div><h3>Prof. Saswata Bhattacharya</h3><p>Professor, Materials Science and Metallurgical Engineering, IIT Hyderabad.</p><div class="profile-links">'+link('https://saswataiith.github.io/','Homepage')+link('https://www.iith.ac.in/msme/saswata/','Institute profile')+'</div></div></article></section>'
for section in [item for item in data['sections'] if item['id'] in ('current', 'former', 'technical-support')]:
    people+=f'<section id="{section["id"]}"><h2>{section["title"]}</h2><div class="people">'+''.join(person_card(p) for p in section['people'])+'</div></section>'
page('people.html','People',people)
page('collaborators.html','Collaborators',heading('WORKING TOGETHER','Our <em>collaborators.</em>','Ideas grow when we explore them together, through experiments, theory and computation.')+'<section><div class="people collaborators">'+''.join(person_card(p,True) for p in data['sections'][2]['people'])+'</div></section><section class="tinted"><h2>When 1 + 1 &gt; 2.</h2><p>Collaboration begins when we bounce ideas off one another. Different experience can reveal an assumption we had overlooked or suggest a question we would not have asked alone. Even apparently similar expertise can lead to very different ways of seeing a problem.</p><p>The connections above are starting points, not fixed divisions of work. Our shared interests evolve through discussion, experiments and modeling. The aim is to develop ideas together that none of us would have reached in isolation.</p></section>')
page('research.html','Research',heading('PHYSICS FIRST','Research &amp; <em>learning.</em>','Compact physical principles can generate remarkably rich microstructures. Our models connect those principles to observations and materials design.')+'<section>'+research+'</section><section class="tinted"><h2>Learn by exploring.</h2><p>Interactive laboratories, derivations and readable simulation examples accompany our research.</p><div class="profile-links">'+link('https://saswataiith.github.io/resources/','Learning resources')+link('https://saswataiith.github.io/publications/','Selected publications')+link('https://saswataiith.github.io/teaching/','Courses and TensorLab')+'</div></section>')
activity=json.loads((root/'data/activity.json').read_text())
life=heading('POSTERS, PHOTOS AND GROUP NEWS','Life in <em>the group.</em>','Research shared, questions discussed and moments together.')
for key,title,empty in [('posters','Research posters','A space for our conference posters and research presentations.'),('photos','Group photos','A space for conferences, lab visits and time together.'),('updates','Group updates','News and milestones from the group.')]:
    life+=f'<section id="{key}"><h2>{title}</h2>'
    if not activity[key]: life+=f'<p>{empty}</p>'
    for item in sorted(activity[key],key=lambda item:item['date'],reverse=True):
        life+=f'<article class="activity"><h3>{escape(item["title"])}</h3><small>{escape(item["date"])} · {escape(item["author"])}</small>'
        if item.get('image'): life+=f'<img src="{escape(item["image"],quote=True)}" alt="{escape(item["alt"],quote=True)}" loading="lazy">'
        life+=f'<p>{escape(item["caption"])}</p>'
        if item.get('file'): life+=link(item['file'],'View poster')
        life+='</article>'
    life+='</section>'
page('group-life.html','Group life',life)
print('Built 5 static pages.')
