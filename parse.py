from bs4 import BeautifulSoup
import re

def parse_content(html_content):
    """Parse HTML content into structured data"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
        element.decompose()
    
    titles = [tag.get_text().strip() for tag in soup.find_all(re.compile('^h[1-6]$'))]
    
    paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
    
    links = []
    for a in soup.find_all('a', href=True):
        link_text = a.get_text().strip()
        link_url = a['href']
        if link_url.startswith('http'): 
            links.append({
                'text': link_text if link_text else link_url,
                'url': link_url
            })

    tables = []
    for table in soup.find_all('table'):
        table_data = {
            'headers': [],
            'rows': []
        }
        
        headers = table.find_all('th')
        if headers:
            table_data['headers'] = [header.get_text().strip() for header in headers]
        else:
            first_row = table.find('tr')
            if first_row:
                cells = first_row.find_all('td')
                table_data['headers'] = [cell.get_text().strip() for cell in cells]
                rows = table.find_all('tr')[1:]
            else:
                rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if cells:
                table_data['rows'].append([cell.get_text().strip() for cell in cells])
        
        if table_data['headers'] or table_data['rows']:
            tables.append(table_data)
    
    return {
        'titles': titles,
        'paragraphs': paragraphs,
        'links': links,
        'tables': tables
    }