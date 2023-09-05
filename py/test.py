# Environment Variables
import os
from dotenv import load_dotenv
load_dotenv()
# Directory
dr = os.getenv("directory")
os.chdir(f"{dr}/py")
import script
nts = script.nts()
do = True
# sh = False
# _ = input("Short? [Y]")
# if _ == 'Y':
sh = True

# while do:
#     show = input('Input Show\n')
#     if show in nts.showlist:
#         nts.runscript([show],short=sh,retry=True)
#     else:
#         dy = input('NOT IN SHOWLIST, DO ANYWAY? [Y/N]')
#         if dy == 'Y':
#             nts.runscript([show],short=sh,retry=True)
#     rd = True
#     while rd:
#         redo = input('\nREDO [SHOW/N]')
#         if redo == 'N':
#             do = False
#             rd = False
#         else:
#             show = redo
#             if show in nts.showlist:
#                 nts.runscript([show],short=sh,retry=True)
#             else:
#                 dy = input('NOT IN SHOWLIST, DO ANYWAY? [Y/N]')
#                 if dy == 'Y':
#                     nts.runscript([show],short=sh,retry=True)

# y = nts._j2d('./yid')
# for i in y:
# if i[0].lower() in ['i','j','k']:
# if i[0].isnumeric():
# print(i)
# try:
#     nts.runner(i,f"./youtube_search_results/{i}",2.5)
#     nts.runner(i,f"./youtube/{i}",3.5)
#     nts.youtubeplaylist(i)
# except Exception as e:
#     print(e)
#     nts.youtubeplaylist(i)
# dos = [i for i in y if i[0].lower() in ['i','j','k']]
# nts.runscript(dos)

# import datetime
# shows = []
# tday = datetime.date.today()
# day = [tday]
# for i in range(1,8):
#     day += [tday - datetime.timedelta(i)]
# for i in nts.showlist:
#     sday = datetime.datetime.fromtimestamp(os.path.getmtime(f"./tracklist/{i}.json")).date()
#     if sday in day:
#         shows += [i]

# shows = ['mount-kimbie','shanticeleste','well-street-records','thea-hd','uline-catalog','sun-cut','tom-boogizm','panorama-yerevan','physical-therapy','red-laser-records','relax-w-reni','stephen-omalley','test-pressing','okonkole-y-trompa','radio-ghibli','british-library-sound-archive','timeisaway','space-afrika','early-bird-show-jack-rollo','early-bird-show-maria-somerville','early-bird-show-spirit-blue','malibu','claire-rousay','the-trilogy-tapes','tommasi','great-southern-lands','suki-sou','claire-milbrath','athens-of-the-north','perfume-advert','mafalda','john-carroll-kirby','jamie-xx','sun-cut','macca','yaeji','carla-dal-forno','soup-to-nuts-lupini','the-breakfast-show-flo','donna-leake','jen-monroe','kaitlyn-aurelia-smith','floating-points','music-4-lovers','fifth-world','rhythmconnection','women-of-british-reggae','diesel-tracks','brassfoot','touching-bass','trevorjackson','guitar-world','under-sleepy-moon','weyes-blood','the-extended-play-sessions','trinh','ash-lauryn','tara-clerkin-trio','haxan-cloak','zach-cowie','whities-w-tasker','victor-kiswell','veronica-vasicka','tropic-of-cancer',"the-new-funk-breakfast-show","space-afrika","calm-roots","sos-radio","sonido-martines","sonic-messengers","show-me-the-body-presents-corpus","sevdaliza","ron-trent","sigourney","ross-allen","relax-w-reni","raga-vibrations","red-laser-records"]
# for i in shows:
#     if i not in nts.showlist:
#         raise RuntimeError(f'{i} not in List')
# # shows = list(nts._j2d('./yid').keys())[::-1]
# nts.runscript(shows)

# shows = nts.showlist
# j = 0
# for i in range(0, len(shows), 5):
#     nts.runscript(shows[j:i]) #[show]
#     j = int(i)

# for show in shows[::-1]:
# for show in nts.showlist:
#     nts.runner(show,f"./spotify/{show}",3)

# nts = script.nts(youtube=False)
# shows = [i for i in nts.showlist]# if i not in ['guests','the-nts-guide-to','in-focus','archive-nights-cafe-oto']]
nts.runscript(nts.showlist[::-1], retry=True)
# for i in nts.showlist[:]:
#     print(i,nts.showlist.index(i),'\n')
#     while True:
#         try:
#             nts.spotifyplaylist(i)
#             break
#         except:
#             nts.runscript([i])
#             pass
