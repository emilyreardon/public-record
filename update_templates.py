import re
import json

NEW_TEMPLATES = {
    1: "The government is ignoring what people actually need and protecting its own power instead. I want my representatives to hold public hearings in every district before passing any new law.",
    2: "We the People should mean every person who lives here, works here, and follows these laws. I want my representatives to update who this country protects so no one is left out.",
    3: "Teaching kids accurate history, even the painful parts, is a protected right. I want my representatives to stop efforts to ban books and restrict what teachers can say in classrooms.",
    4: "I believe in the right to own a gun and in universal background checks. Both can be true. I want my representatives to require background checks for every gun sale.",
    5: "The government should never move military or police into a neighborhood without the people who live there agreeing. I want my representatives to require community consent before any federal presence in local areas.",
    6: "My phone, my location, and my medical records are private. I want my representatives to update privacy laws so digital information gets the same protection as my home.",
    7: "People should not lose their property to the government unless they are convicted of a crime. I want my representatives to end civil asset forfeiture.",
    8: "People sit in jail for years before their trial because they cannot afford bail. I want my representatives to end cash bail and guarantee every person a truly speedy trial.",
    9: "Corporations force customers into private arbitration and take away their right to a jury trial. I want my representatives to ban forced arbitration clauses in consumer contracts.",
    10: "Solitary confinement causes permanent mental damage and is cruel punishment. I want my representatives to ban it for juveniles and limit it to 15 days for adults.",
    11: "The right to make decisions about my own body belongs to me, not the government. I want my representatives to protect bodily autonomy as a constitutional right.",
    12: "States should be able to set stricter environmental standards than the federal government. I want my representatives to protect states' rights to go further on clean energy and clean water.",
    13: "Citizens should be able to sue their state government when their rights are violated. I want my representatives to limit state immunity so people can hold their government accountable in court.",
    14: "Candidates who lose the popular vote should not be able to win the presidency. I want my representatives to eliminate the Electoral College and elect the president by national popular vote.",
    15: "The 13th Amendment still allows forced labor as punishment for a crime. I want my representatives to close this loophole so no one can be made to work for nothing.",
    16: "Children born in this country are citizens, full stop. I want my representatives to protect birthright citizenship from being taken away by executive order.",
    17: "Voter ID laws and fewer polling places in minority neighborhoods make it harder to vote. I want my representatives to restore the full Voting Rights Act.",
    18: "The wealthiest Americans pay a lower tax rate than teachers and nurses. I want my representatives to pass a minimum tax on billionaires so everyone pays their fair share.",
    19: "Every American should directly elect their senators with equal weight. I want my representatives to end the filibuster so the majority's votes actually count.",
    20: "Banning things people want rarely works and fills prisons instead. I want my representatives to move drug policy toward treatment and harm reduction instead of criminalization.",
    21: "Women and nonbinary people still face barriers at the ballot box and in government. I want my representatives to pass the Equal Rights Amendment.",
    22: "The time between an election and inauguration is too long and too dangerous. I want my representatives to shorten the transition period to 30 days.",
    23: "Laws that stop working should be repealed. I want my representatives to decriminalize marijuana federally and expunge the records of everyone convicted under those old laws.",
    24: "No one should hold any federal office for more than 12 years. I want my representatives to pass term limits for Congress.",
    25: "People in Washington DC pay federal taxes but have no voting voice in Congress. I want my representatives to make DC a state.",
    26: "Any fee or ID cost that stands between a person and their vote is a poll tax. I want my representatives to make voting ID free and easy to get for every citizen.",
    27: "When a president cannot do their job, Congress needs clear and fast rules for what happens next. I want my representatives to strengthen the 25th Amendment so there is no confusion.",
    28: "Young people pay taxes, serve in the military, and live with the consequences of elections they cannot vote in. I want my representatives to lower the voting age to 16.",
    29: "Members of Congress should not be able to vote themselves a raise. I want my representatives to tie congressional pay to the federal minimum wage.",
    30: "Public health decisions should follow scientific evidence, not be shaped by lobbying. I want my representatives to require independent review before any rule that affects health or safety is weakened.",
    31: "A divided country is easier to take advantage of. I want my representatives to prioritize what we share over what divides us when setting foreign policy.",
    32: "Cyberattacks on our elections are a real and growing threat. I want my representatives to fund independent election security in every state.",
    33: "One state making its own deals with foreign countries weakens everyone. I want my representatives to make sure all international agreements go through Congress.",
    34: "When states fight each other, other countries benefit. I want my representatives to create federal rules that keep states cooperating instead of competing against each other.",
    35: "States giving away tax breaks to lure corporations hurts workers in every state. I want my representatives to stop companies from playing states against each other.",
    36: "States hoarding water from rivers that cross their borders causes real harm downstream. I want my representatives to create a federal water-sharing plan before the next drought.",
    37: "Building up the military without also building alliances makes us less safe. I want my representatives to fully fund diplomacy alongside defense.",
    38: "Small groups taking over local governments and spreading fear is a real danger. I want my representatives to protect local elections from outside money and interference.",
    39: "Gerrymandering lets politicians pick their voters instead of voters picking their representatives. I want my representatives to require independent redistricting in every state.",
    40: "Trade agreements should protect American workers, not just corporations. I want my representatives to include enforceable labor standards in every trade deal.",
    41: "A country that cannot fund its own government is not truly self-governing. I want my representatives to pass a budget on time, every year, with full transparency.",
    42: "Wasteful government spending hurts everyone who pays taxes and everyone who needs services. I want my representatives to require independent audits of every major federal program.",
    43: "This country is big and complicated, but every citizen deserves equal representation. I want my representatives to make sure rural and urban communities both have a real voice in Congress.",
    44: "A government that cannot enforce its own laws is not really in charge. I want my representatives to give federal agencies the tools they need to actually follow through.",
    45: "The federal government should handle the things states cannot do alone, like pandemics and climate. I want my representatives to fund national programs that work across state lines.",
    46: "Local governments know their communities better than Washington does. I want my representatives to give cities and counties more control over how federal money gets spent locally.",
    47: "Some states are much more powerful than others because of their size and money. I want my representatives to create fairer rules so smaller states are not ignored.",
    48: "Alliances between states make everyone stronger. I want my representatives to encourage interstate cooperation on climate, infrastructure, and public health.",
    49: "A weak federal government lets powerful interests fill the gap. I want my representatives to strengthen federal oversight of industries that affect every state.",
    50: "When the national government fails, ordinary people pay the price. I want my representatives to fix what is broken in our federal system before the next crisis hits.",
    51: "Every American should be able to trust that federal law applies equally in every state. I want my representatives to close loopholes that let some states ignore national standards.",
    52: "The federal government should be strong enough to protect people, but not so powerful it controls everything. I want my representatives to protect both individual rights and the common good.",
    53: "National defense should protect every American, not just those near military bases. I want my representatives to fund cybersecurity and disaster response as seriously as traditional military.",
    54: "The military should not have a permanent presence in communities that do not want it. I want my representatives to require congressional approval before any long-term military deployment.",
    55: "Military spending decisions should be made in public, not in secret. I want my representatives to require a full public audit of the defense budget every year.",
    56: "Civil liberties should not disappear during a national emergency. I want my representatives to set clear time limits on any emergency powers granted to the president.",
    57: "When the government uses emergency powers, it must tell the public exactly what it is doing and why. I want my representatives to require transparency for every executive action taken in a crisis.",
    58: "The National Guard should be under community control, not used against the community. I want my representatives to require state and local approval before any Guard deployment in a city.",
    59: "Taxes should pay for things everyone uses, like roads, schools, and clean water. I want my representatives to make the tax system simpler and more fair for working families.",
    60: "The federal government's power to tax should come with a duty to spend that money wisely. I want my representatives to pass a law requiring every dollar to be tracked publicly.",
    61: "Both federal and state governments need money to work. I want my representatives to stop passing laws that shift costs to states without sending the funding to pay for them.",
    62: "Tax laws should not be written by the industries being taxed. I want my representatives to ban corporate lobbyists from drafting the legislation that governs them.",
    63: "Everyone who benefits from this country should help pay for it. I want my representatives to close offshore tax loopholes so corporations cannot avoid their fair share.",
    64: "When the wealthy pay less in taxes than the poor, something is wrong. I want my representatives to flatten the tax code so every income level pays a fair rate.",
    65: "Local governments need stable funding to provide basic services. I want my representatives to protect revenue sharing so cities and counties can do their jobs.",
    66: "Writing a government that works for everyone is hard and takes compromise. I want my representatives to hold public hearings before any major constitutional change.",
    67: "Our constitution was designed to be improved over time. I want my representatives to take the amendment process seriously instead of avoiding hard questions.",
    68: "A government that is both national and made of states is a hard balance. I want my representatives to protect both federal authority and state rights without letting either take over.",
    69: "The people who wrote the Constitution made deals they knew were wrong. I want my representatives to finish the work of making this document true for everyone.",
    70: "The government's powers should fit the problems it needs to solve. I want my representatives to update federal authority so it can handle modern challenges like climate change and cybersecurity.",
    71: "Foreign policy should be made in public, not in private. I want my representatives to require congressional debate before any military action or major treaty.",
    72: "The rules of government should work for everyone, not just for those already in power. I want my representatives to protect the right of every citizen to participate in democracy.",
    73: "No state should be able to block rights that federal law guarantees to all citizens. I want my representatives to enforce federal civil rights laws in every state without exception.",
    74: "States should handle their own affairs, but not at the expense of other states or their own residents. I want my representatives to draw a clear line between state and federal responsibility.",
    75: "The federal government protects rights that states sometimes try to take away. I want my representatives to make clear that federal law is the floor, not the ceiling, for civil rights.",
    76: "No one branch of government should be able to do whatever it wants. I want my representatives to strengthen the checks between Congress, the president, and the courts.",
    77: "When one branch gets too powerful, everyone suffers. I want my representatives to pass new laws that enforce the balance of power the Constitution requires.",
    78: "Congress should not be able to ignore court rulings it disagrees with. I want my representatives to pass a law requiring the executive branch to enforce every Supreme Court decision.",
    79: "The people should have a direct say in how their government is structured. I want my representatives to hold a national public comment period before any constitutional amendment is voted on.",
    80: "The government works best when no single person or group can control everything. I want my representatives to strengthen every check and balance in our system before it is needed.",
    81: "Representatives should actually represent the people who live in their district, not donors from other states. I want my representatives to require full residency and limit out-of-district fundraising.",
    82: "Two-year terms keep representatives focused on the next election instead of the next generation. I want my representatives to consider four-year terms with stronger accountability measures.",
    83: "The way states count people to assign representatives still leaves some communities without a real voice. I want my representatives to count every person, including non-citizens, in the census.",
    84: "A House of Representatives with 435 members cannot truly represent 335 million people. I want my representatives to expand the House so every district is small enough to know its member.",
    85: "Representatives who never visit their district are not representing it. I want my representatives to require a minimum number of in-person town halls in their home communities each year.",
    86: "Wealthy donors should not have more access to their representatives than ordinary citizens. I want my representatives to ban members of Congress from meeting privately with lobbyists.",
    87: "The House should grow as the country grows. I want my representatives to pass a law that automatically increases the size of the House every decade based on population.",
    88: "Congress should not be able to set its own election rules in a way that helps the party in power. I want my representatives to create a nonpartisan election rules commission.",
    89: "Partisan control of election administration is a threat to fair results. I want my representatives to require nonpartisan administration of all federal elections.",
    90: "Every citizen should have equal access to voting regardless of which state they live in. I want my representatives to pass national minimum standards for polling hours, locations, and registration.",
    91: "Two senators per state means Wyoming has 70 times more Senate power than California. I want my representatives to reform Senate rules so every American's vote counts more equally.",
    92: "The Senate was designed to slow things down, but it has become a place where needed laws go to die. I want my representatives to reform the filibuster so the majority can actually govern.",
    93: "Treaties that affect every American should require a full Senate debate and public hearings. I want my representatives to make the treaty process more transparent and participatory.",
    94: "Impeachment should be a real check on power, not a partisan tool. I want my representatives to pass clearer rules for what counts as an impeachable offense.",
    95: "When the Senate sits as a jury in an impeachment trial, it should follow the same rules as any other jury. I want my representatives to require senators to hear all the evidence before voting.",
    96: "The president should not be able to appoint judges, ambassadors, or cabinet members without real Senate review. I want my representatives to restore full confirmation hearings for every major appointment.",
    97: "The person who becomes president should be chosen by the most voters, not by geography. I want my representatives to reform the Electoral College so every vote counts equally.",
    98: "The president has powers that were meant for emergencies but are now used routinely. I want my representatives to pass a law requiring congressional approval for any extended use of emergency powers.",
    99: "One person should not be able to make decisions about war, trade, and public health without accountability. I want my representatives to claw back congressional authority over these decisions.",
    100: "Short presidential terms make long-term problems impossible to solve. I want my representatives to consider a single six-year term so presidents can focus on governing instead of campaigning.",
    101: "Presidents who spend their whole second term running for reelection serve their party, not the public. I want my representatives to pass a constitutional amendment limiting presidents to one term.",
    102: "Congress should not give the president money with no strings attached. I want my representatives to require specific spending authorizations for every dollar the executive branch spends.",
    103: "The president's power to pardon should not extend to themselves or their co-conspirators. I want my representatives to pass a law closing the self-pardon loophole.",
    104: "Treaties that commit American lives and resources should require full congressional debate. I want my representatives to pass a law requiring Senate ratification for any agreement that involves military force.",
    105: "Presidential appointments shape this country for decades. I want my representatives to require public hearings for every federal judge and cabinet secretary before they are confirmed.",
    106: "The president has too much power to make rules without Congress. I want my representatives to review all existing executive orders and require congressional approval for any that act like laws.",
    107: "Supreme Court justices serve for life while the country changes around them. I want my representatives to pass an 18-year term limit for all federal judges.",
    108: "Federal judges should have to follow the same ethics rules as everyone else in government. I want my representatives to pass a binding code of conduct for all federal judges, including the Supreme Court.",
    109: "Courts should be able to hear cases from people who were harmed by their government, even if the government did not want to be sued. I want my representatives to limit judicial immunity.",
    110: "Criminal and civil courts should have enough judges to hear cases within a reasonable time. I want my representatives to fill every vacant federal judgeship and add new seats where there is a backlog.",
    111: "State and federal courts should not be able to dismiss civil rights cases on technical grounds before hearing the facts. I want my representatives to reform qualified immunity.",
    112: "The right to a jury trial in civil cases is being quietly eliminated by forced arbitration. I want my representatives to restore the right to a jury for disputes involving consumer and employment law.",
    113: "The Constitution should protect the right to a clean environment, affordable healthcare, and a good education. I want my representatives to pass a 28th Amendment that makes these rights real.",
    114: "The best time to fix the Constitution is before a crisis, not during one. I want my representatives to hold a national debate about what the Constitution still needs to say.",
    115: "The 13th Amendment still allows slavery as punishment for a crime, and prisons use it every day. I want my representatives to close this loophole so no one can be forced to work for nothing.",
    116: "Equal protection under the law should mean the same quality of school, hospital, and road for every American. I want my representatives to enforce the 14th Amendment where it has been ignored.",
    117: "If the broader version of the 15th Amendment had passed, voting would be easier for more people today. I want my representatives to pass a new voting rights law that protects every citizen.",
    118: "Women won the right to vote in 1920, but many were blocked until 1965 and some face new barriers today. I want my representatives to protect every woman's right to vote from new restrictions.",
    119: "Any fee, fine, or ID cost that stands between a person and their vote is a poll tax, no matter what it is called. I want my representatives to make voting free and accessible for every citizen.",
    120: "Young people are paying for climate change, student debt, and war with decisions they had no vote in. I want my representatives to lower the voting age to 16.",
    121: "The Civil Rights Act made discrimination illegal but enforcement is still too weak to work. I want my representatives to fully fund the Equal Employment Opportunity Commission.",
    122: "The Supreme Court gutted the Voting Rights Act in 2013. I want my representatives to pass a new law that restores full voting protections for every American.",
    123: "Locking up American citizens because of their heritage was wrong in 1942 and would be wrong today. I want my representatives to pass a law preventing mass detention based on race, religion, or national origin.",
    124: "The president can order fairness in federal hiring with one signature. I want my representatives to push for an executive order ending discrimination in all federal contracts right now.",
    125: "Schools still cut girls' sports programs and look the other way on harassment. I want my representatives to enforce Title IX with real consequences for schools that break the law.",
    126: "I live on land that was taken without consent. I want my representatives to work with the Lenape Nation to honor what the government promised and then broke.",
    127: "The United States has broken nearly every treaty it signed with Native nations. I want my representatives to honor what is left of those agreements and stop breaking new ones.",
    128: "Thousands of Cherokee people died on the Trail of Tears because the government forced through a treaty and then ignored it. I want my representatives to restore tribal land rights and sovereignty.",
    129: "The Supreme Court once ruled that Black people had no rights the government had to respect. I want my representatives to make sure that kind of ruling can never happen again.",
    130: "Separate is never equal, and unequal school funding proves it every day. I want my representatives to fund every public school equally so every child gets the same start.",
    131: "The Supreme Court upheld Japanese internment and has never formally overturned it. I want my representatives to pass a law making clear that mass detention based on race or religion is unconstitutional.",
    132: "Women were written out of the Declaration of Independence on purpose. I want my representatives to pass the Equal Rights Amendment so the Constitution finally protects everyone.",
    133: "Freedom means something different depending on who you are in this country. I want my representatives to take seriously the parts of American history we have not yet made right.",
    134: "Black women are still paid less and protected less than almost anyone else in this country. I want my representatives to pass pay equity laws with real enforcement and real penalties.",
    135: "The Nez Perce were promised their land and had it taken anyway. I want my representatives to restore federal recognition and land rights for Native nations whose treaties were broken.",
    136: "Disabled Americans sat in a federal building for 25 days to make the government follow its own law. I want my representatives to fully fund ADA and Section 504 enforcement so no one has to do that again.",
    137: "40 million Americans live in poverty in the wealthiest country in history. I want my representatives to pass a living wage and guaranteed healthcare for every person.",
}

filepath = "/sessions/awesome-gracious-euler/mnt/public-record-project/submit.html"

with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

# Find the CORPUS JSON array
match = re.search(r'(const CORPUS = )(\[.*?\])(;)', html, re.DOTALL)
if not match:
    raise ValueError("Could not find CORPUS array in submit.html")

prefix = match.group(1)
corpus_json = match.group(2)
suffix = match.group(3)

corpus = json.loads(corpus_json)

updated_count = 0
for item in corpus:
    item_id = item.get("id")
    if item_id in NEW_TEMPLATES:
        item["submit_template"] = NEW_TEMPLATES[item_id]
        updated_count += 1

print(f"Updated {updated_count} templates out of {len(corpus)} items.")

# Verify first 3 updated templates
print("\nFirst 3 updated templates:")
for item in corpus[:3]:
    print(f"  id={item['id']}: {item.get('submit_template', '(no template)')[:80]}...")

# Serialize back
new_corpus_json = json.dumps(corpus, ensure_ascii=False)

# Replace in HTML
new_html = html[:match.start()] + prefix + new_corpus_json + suffix + html[match.end():]

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_html)

print("\nDone.")
