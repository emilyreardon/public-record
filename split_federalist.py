import os, re, glob

FED_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "core", "federalist")

TITLES = {
1:"General Introduction",2:"Concerning Dangers from Foreign Force and Influence",
3:"The Same Subject Continued: Concerning Dangers From Foreign Force and Influence",
4:"The Same Subject Continued: Concerning Dangers From Foreign Force and Influence",
5:"The Same Subject Continued: Concerning Dangers from Foreign Force and Influence",
6:"Concerning Dangers from Dissensions Between the States",
7:"The Same Subject Continued: Concerning Dangers from Dissensions Between the States",
8:"The Consequences of Hostilities Between the States",
9:"The Utility of the Union as a Safeguard Against Domestic Faction and Insurrection",
10:"The Same Subject Continued: The Union as a Safeguard Against Domestic Faction and Insurrection",
11:"The Utility of the Union in Respect to Commercial Relations and a Navy",
12:"The Utility of the Union In Respect to Revenue",
13:"Advantage of the Union in Respect to Economy in Government",
14:"Objections to the Proposed Constitution from Extent of Territory Answered",
15:"The Insufficiency of the Present Confederation to Preserve the Union",
16:"The Same Subject Continued: The Insufficiency of the Present Confederation to Preserve the Union",
17:"The Same Subject Continued: The Insufficiency of the Present Confederation to Preserve the Union",
18:"The Same Subject Continued: The Insufficiency of the Present Confederation to Preserve the Union",
19:"The Same Subject Continued: The Insufficiency of the Present Confederation to Preserve the Union",
20:"The Same Subject Continued: The Insufficiency of the Present Confederation to Preserve the Union",
21:"Other Defects of the Present Confederation",
22:"The Same Subject Continued: Other Defects of the Present Confederation",
23:"The Necessity of a Government as Energetic as the One Proposed to the Preservation of the Union",
24:"The Powers Necessary to the Common Defense Further Considered",
25:"The Same Subject Continued: The Powers Necessary to the Common Defense Further Considered",
26:"The Idea of Restraining the Legislative Authority in Regard to the Common Defense Considered",
27:"The Same Subject Continued: The Idea of Restraining the Legislative Authority in Regard to the Common Defense Considered",
28:"The Same Subject Continued: The Idea of Restraining the Legislative Authority in Regard to the Common Defense Considered",
29:"Concerning the Militia",
30:"Concerning the General Power of Taxation",
31:"The Same Subject Continued: Concerning the Power of Taxation",
32:"The Same Subject Continued: Concerning the Power of Taxation",
33:"The Same Subject Continued: Concerning the Power of Taxation",
34:"The Same Subject Continued: Concerning the Power of Taxation",
35:"The Same Subject Continued: Concerning the Power of Taxation",
36:"The Same Subject Continued: Concerning the Power of Taxation",
37:"Concerning the Difficulties of the Convention in Devising a Proper Form of Government",
38:"Incoherence of the Objections to the New Plan Exposed",
39:"Conformity of the Plan to Republican Principles",
40:"The Powers of the Convention to Form a Mixed Government Examined and Sustained",
41:"General View of the Powers Conferred by the Constitution",
42:"The Powers Conferred by the Constitution Further Considered",
43:"The Same Subject Continued: The Powers Conferred by the Constitution Further Considered",
44:"Restrictions on the Authority of the Several States",
45:"The Alleged Danger From the Powers of the Union to the State Governments Considered",
46:"The Influence of the State and Federal Governments Compared",
47:"The Particular Structure of the New Government and Distribution of Power Among Its Different Parts",
48:"These Departments Should Not Be So Far Separated as to Have No Constitutional Control Over Each Other",
49:"Method of Guarding Against the Encroachments of Any One Department of Government by Appealing to the People Through a Convention",
50:"Periodic Appeals to the People Considered",
51:"The Structure of the Government Must Furnish the Proper Checks and Balances Between the Different Departments",
52:"The House of Representatives",
53:"The Same Subject Continued: The House of Representatives",
54:"The Apportionment of Members Among States",
55:"The Total Number of the House of Representatives",
56:"The Same Subject Continued: The Total Number of the House of Representatives",
57:"The Alleged Tendency of the Plan to Elevate the Few at the Expense of the Many Considered in Connection with Representation",
58:"Objection that the Number of Members Will Not Be Augmented as the Progress of Population Demands Considered",
59:"Concerning the Power of Congress to Regulate the Election of Members",
60:"The Same Subject Continued: Concerning the Power of Congress to Regulate the Election of Members",
61:"The Same Subject Continued: Concerning the Power of Congress to Regulate the Election of Members",
62:"The Senate",
63:"The Senate Continued",
64:"The Powers of the Senate",
65:"The Powers of the Senate Continued",
66:"Objections to the Power of the Senate To Set as a Court for Impeachments Further Considered",
67:"The Executive Department",
68:"The Mode of Electing the President",
69:"The Real Character of the Executive",
70:"The Executive Department Further Considered",
71:"The Duration in Office of the Executive",
72:"The Same Subject Continued, and Re-Eligibility of the Executive Considered",
73:"The Provision for Support of the Executive, and the Veto Power",
74:"The Command of the Military and Naval Forces, and the Pardoning Power of the Executive",
75:"The Treaty Making Power of the Executive",
76:"The Appointing Power of the Executive",
77:"The Appointing Power Continued and Other Powers of the Executive Considered",
78:"The Judiciary Department",
79:"The Judiciary Continued",
80:"The Powers of the Judiciary",
81:"The Judiciary Continued, and the Distribution of Judicial Authority",
82:"The Judiciary Continued",
83:"The Judiciary Continued in Relation to Trial by Jury",
84:"Certain General and Miscellaneous Objections to the Constitution Considered and Answered",
85:"Concluding Remarks",
}

AUTHORS = {}
for n in [1,6,7,8,9,11,12,13,15,16,17,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,59,60,61,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85]:
    AUTHORS[n] = "Alexander Hamilton"
for n in [10,14,37,38,39,40,41,42,43,44,45,46,47,48,58]:
    AUTHORS[n] = "James Madison"
for n in [2,3,4,5,64]:
    AUTHORS[n] = "John Jay"
for n in [18,19,20]:
    AUTHORS[n] = "Alexander Hamilton and James Madison"
for n in [49,50,51,52,53,54,55,56,57,62,63]:
    AUTHORS[n] = "Alexander Hamilton or James Madison"

def slugify(n):
    return "federalist_" + str(n).zfill(2) + ".md"

def find_marker_positions(text):
    positions = []
    for m in re.finditer(r"Federalist No\.\s*(\d+)", text):
        num = int(m.group(1))
        positions.append((num, m.start()))
    return positions

def dedupe_first_occurrence(positions):
    seen = {}
    for num, pos in positions:
        if num not in seen:
            seen[num] = pos
    return seen

written = 0
skipped_existing = 0
missing = []

files = sorted(glob.glob(os.path.join(FED_DIR, "*_extracted.txt")))
combined = ""
offsets = []
for fp in files:
    with open(fp, encoding="utf-8") as f:
        content = f.read()
    offsets.append((len(combined), fp))
    combined += "\n" + content

positions = find_marker_positions(combined)
first_seen = dedupe_first_occurrence(positions)
sorted_nums = sorted(first_seen.keys())

for i, num in enumerate(sorted_nums):
    if num < 1 or num > 85:
        continue
    start = first_seen[num]
    end = first_seen[sorted_nums[i+1]] if i+1 < len(sorted_nums) else len(combined)
    chunk = combined[start:end].strip()

    out_path = os.path.join(FED_DIR, slugify(num))
    if os.path.exists(out_path):
        skipped_existing += 1
        continue

    title = TITLES.get(num, "")
    author = AUTHORS.get(num, "")

    header = "---\n"
    header += "title: Federalist No. " + str(num) + (" (" + title + ")" if title else "") + "\n"
    header += "tier: core\n"
    header += "doc_type: federalist_paper\n"
    header += "date: 1787-1788\n"
    header += "citation: The Federalist No. " + str(num) + (" (" + author + ")" if author else "") + "\n"
    header += "source_url: https://guides.loc.gov/federalist-papers/full-text\n"
    header += "source_name: Library of Congress (Federalist Papers guide, text from Project Gutenberg e-text)\n"
    header += "retrieval_tags: [federalist, ratification, constitution, publius]\n"
    header += "paired_with: []\n"
    header += "mobile_piece: resin_tablet\n"
    header += "verified: false\n"
    header += "---\n\n"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + chunk + "\n")
    written += 1
    print("wrote " + slugify(num))

print("")
print("=== summary ===")
print("written: " + str(written))
print("already existed, skipped: " + str(skipped_existing))
found_nums = set(sorted_nums)
missing_nums = [n for n in range(1,86) if n not in found_nums]
print("missing (not found in source pages): " + str(missing_nums))
