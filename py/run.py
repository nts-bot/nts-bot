# Environment Variables
from dotenv import load_dotenv
load_dotenv()
import warnings
warnings.filterwarnings("ignore")
# Directory
import os
dr = os.getenv("directory")
os.chdir(f"{dr}/py")
import script
nts = script.nts()
# nts.wait('connect',False)
# soup = nts.browse("https://www.nts.live/nts-picks",amount=100) 
soup = nts.browse("https://www.nts.live/latest",amount=30) #15
episodes = soup.select('a.nts-grid-v2-item__header')
shelf = dict()
for i in episodes:
    href = i['href']
    show = href.split('/')[2]
    epis = href.split('/')[-1]
    if show not in shelf:
        shelf[show] = [epis]
        
nts.runscript(list(shelf.keys()),retry=True)#,bd=False,short=False,retry=True)
