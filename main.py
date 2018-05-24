import sys
import re
from xml.dom import minidom
from urllib.request import urlopen

queue = []
urls = []


def check_url(arg):
    if 'http://' in arg or 'https://' in arg:
        return True
    return False


def check_xml(arg):
    table = arg.split('.')
    if table[-1] == 'xml':
        return True
    return False


def spider(mainurl):
    url = queue[0]
    if url not in urls:
        urls.append(url)
        queue.remove(url)
    request = urlopen(url)
    page = request.read()
    reg = re.compile(b'<a [^>]*href=[\'|"](.*?)[\'"][^>]*?>')
    tags = reg.findall(page)
    for e in tags:
        if "b'/" in str(e) and '#' not in str(e):
            local = mainurl + str(e).split("'")[1]
            if local not in queue and local not in urls:
                queue.append(local)


def search_site(mainurl):
    while len(queue) > 0:
        spider(mainurl)


def to_if(name):
    if name == "Jan":
        return '01'
    elif name == "Feb":
        return '02'
    elif name == "Mar":
        return '03'
    elif name == "Apr":
        return '04'
    elif name == "May":
        return '05'
    elif name == "Jun":
        return '06'
    elif name == "Jul":
        return '07'
    elif name == "Aug":
        return '08'
    elif name == "Sep":
        return '09'
    elif name == "Oct":
        return '10'
    elif name == "Nov":
        return '11'
    else:
        return '12'


def calculate_priority(url):
    data = url.split('/')
    deep = len(data) - 3
    return str(1 - (deep * 0.08))


def check_data(url):
    request = urlopen(url)
    info = bytes(request.info())
    reg = re.compile(b'Last-Modified:[^\n]+')
    tags = reg.findall(info)
    date = str(tags[0]).split(' ')
    return (date[4] + '-' + to_if(date[3]) + '-' + date[2] + 'T' + date[5] + '+00:00')


def generate_xml(filename):
    doc = minidom.Document()
    root = doc.createElement('urlset')
    root.setAttribute('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation',
                      'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
    doc.appendChild(root)

    for u in urls:
        tagurl = doc.createElement('url')

        loc = doc.createElement('loc')
        text = doc.createTextNode(u)
        loc.appendChild(text)
        tagurl.appendChild(loc)

        lastmod = doc.createElement('lastmod')
        date = doc.createTextNode(check_data(u))
        lastmod.appendChild(date)
        tagurl.appendChild(lastmod)

        priority = doc.createElement('priority')
        value = doc.createTextNode(calculate_priority(u))
        priority.appendChild(value)
        tagurl.appendChild(priority)

        root.appendChild(tagurl)

    xml_str = doc.toprettyxml(indent="  ", encoding="utf-8").decode(encoding="utf-8")
    with open(filename, "w") as f:
        f.write(xml_str)


def main(argv):
    if len(argv) != 2:
        print('Try again: python main.py <main url> <name.xml>')
        return

    if not check_url(argv[0]):
        print('Try again: input must start with http:// or https://')

    if not check_xml(argv[1]):
        print('Try again: output file must be *.xml')

    print('Web spider started..\n')
    queue.append(argv[0])
    search_site(argv[0])
    print('XML generator started..\n')
    generate_xml(argv[1])
    print(argv[1], ' created correctly')


if __name__ == "__main__":
    main(sys.argv[1:])
