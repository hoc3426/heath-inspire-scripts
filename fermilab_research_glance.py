from invenio.search_engine import perform_request_search
import time
import bitly
import re
import os

YEAR   = int(time.strftime('%Y'))
YEAR_1 = str(YEAR - 1)
YEAR_2 = str(YEAR - 2)
YEAR   = str(YEAR)

MONTH     = int(time.strftime('%m'))
MONTH_1   = MONTH - 1
MONTH_2   = MONTH - 2

if MONTH == 1:
    MONTH   = YEAR   + '-01'
    MONTH_1 = YEAR_1 + '-12'
    MONTH_2 = YEAR_1 + '-11'
elif MONTH == 2:
    MONTH   = YEAR   + '-02'
    MONTH_1 = YEAR   + '-01'
    MONTH_2 = YEAR_1 + '-12'
else:
    fmonth = lambda x: '-0' + str(x) if x < 10 else '-' + str(x)
    MONTH   = YEAR + fmonth(MONTH)
    MONTH_1 = YEAR + fmonth(MONTH_1)
    MONTH_2 = YEAR + fmonth(MONTH_2)

os.environ['TZ'] = 'CEST+5'
DATE_TIME_STAMP = time.strftime('%Y-%m-%d %H:%M:%S')
DATE_STAMP      = time.strftime('%Y-%m-%d')



BITLY_KEY = 'R_4165e9efdb444469a6dd475b52f16b87'
BITLY_ACCOUNT = 'hoc3426'
API = bitly.Api(login = BITLY_ACCOUNT, apikey = BITLY_KEY)



def main():

    groups = ['All', 'E', 'CMS', 'T', 'A', 'AE', 'PPD', 'AD/APC']
    groups += ['TD', 'CD', 'Other']
    docs = ['All', 'PUB', 'THESIS', 'CONF', 'TM', 'FN']
    dates = [YEAR_2, YEAR_1, YEAR, MONTH_2, MONTH_1, MONTH]
    filename = 'fermilab_research_glance.html'
    filename_w = 'www/' + filename
    output = open(filename_w,'w')
    output.write('<!doctype html>\n')
    output.write('<html lang="en">\n')
    output.write('<head>\n')
    output.write('  <meta charset="utf-8">\n')
    output.write('  <title>FERMILAB RESEARCH AT A GLANCE</title>\n')
    output.write('  <style>\n')
    output.write('  td {\n')
    output.write('      text-align: right;\n')
    output.write('  }\n')
    output.write('  td.l {\n')
    output.write('      text-align: left;\n')
    output.write('      padding: 7px;\n')
    output.write('  }\n')
    output.write('  </style>\n')
    output.write('  </meta\n')
    output.write('</head>\n')
    output.write('<body>\n')
    output.write('<p><a href="http://ccd.fnal.gov/techpubs/fermilab_spires.html">\n')
    output.write('Fermilab Technical Publications</a></p>\n')
    output.write('<h3>FERMILAB RESEARCH AT A GLANCE</h3>\n')
    output.write('<p>Glossary at end.</p>\n')
    output.write('<p><i>Updated: ' + DATE_TIME_STAMP + '</i></p>\n')
    output.write('<table>\n')
    output.write('<tr>\n')
    output.write('<td></td>\n')
    output.write('<td>Date</td>\n')
    for group in groups:
        if group == 'A':
            group = 'AT'
        output.write('<td>' + group + '</td>\n')
    output.write('</tr>\n')

    for doc in docs:
        output.write('<tr>\n')
        output.write('<td>' + doc + '</td>\n')
        output.write('<td>\n')
        output.write('<ul>\n')
        for date in dates:
            output.write('<li>' + date + '</li>\n')
            if date == YEAR or date == MONTH:
                #output.write('<br />\n')
                output.write('</ul>\n')
                output.write('<ul>\n')
        output.write('</ul>\n')
        output.write('</td>\n')
        for group in groups:
            output.write('<td>\n')
            output.write('<ul>\n')
            for date in dates:
                if group == 'All':
                    group = ''
                if doc == 'All':
                    doc = ''
                search  = 'find r fermilab ' + doc
                if group == 'Other':
                    for good_group in groups[1:len(groups)-1]:
                        if good_group == 'AD/APC':
                            search += ' not  (r AD or APC)'
                        else:
                            search += ' not r ' + good_group
                elif group == 'AD/APC':
                    search  = 'find r fermilab ' + doc + ' and (r AD or APC)'
                else:
                    search  += ' ' + group
                search += ' and de ' + date
                search = re.sub(r'\s+', ' ', search)
                result = perform_request_search(p=search, cc="HEP")
                result = len(result)
                if result == 0:
                    line = "<li></li>\n"
                else:
                    link = search.replace(' ','+')
                    link = 'http://inspirehep.net/search?p=' + link
                    link += '&rg=100&sf=earliestdate'
                    try:
                        link = API.shorten(link)
                    except:
                        pass
                    line = '<li> <a href=\"' + link + '\">'
                    line += str(result) + '</a> </li>'
                output.write(line + '\n')
                if date == YEAR or date == MONTH:
                    #output.write('<br />')
                    output.write('</ul>\n')
                    output.write('<ul>\n')
            output.write('</ul>\n')
            output.write('</td>\n')
        output.write('</tr>\n')
    output.write('</table>\n')

    output.write('<h4>Glossary</h4>\n')
    output.write('<table>\n')
    output.write('<tr>\n')
    output.write('<td class="l">E: Experimental papers</td>\n')
    output.write('<td class="l">PPD: Particle Physics Division papers</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">T: Particle Physics Division Theoretical Physics Department papers</td>\n')
    output.write('<td class="l">AD/APC: Accelerator Division and Accelerator Physics Center papers</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">AT: Fermilab Center for Particle Astrophysics theoretical papers</td>\n')
    output.write('<td class="l">TD: Technical Division papers</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">AE: Fermilab Center for Particle Astrophysics experimental papers</td>\n')
    output.write('<td class="l">CD: Computing Sector papers</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l"> </td>\n')
    output.write('<td class="l"> </td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l"> </td>\n')
    output.write('<td class="l"> </td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l"> </td>\n')
    output.write('<td class="l"> </td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">PUB: Paper intended for publication in a journal</td>\n')
    output.write('<td class="l">TM: Technical memo</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">CONF: Paper written as part of a conference</td>\n')
    output.write('<td class="l">FN: Physics note - short paper not fitting the other categories</td>\n')
    output.write('</tr>\n')
    output.write('<tr>\n')
    output.write('<td class="l">THESIS: Ph.D. thesis based on work done at Fermilab</td>\n')
    output.write('<td class="l"></td>\n')
    output.write('</tr>\n')
    output.write('</table>\n')
    output.write('</body>\n')
    output.write('</html>\n')
    output.close()
    print 'cd /afs/fnal.gov/files/expwww/bss/html/techpubs'
    print '\\rm ' + filename
    print 'wget http://hoc.web.cern.ch/hoc/' + filename

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

