import re
import os
from html.parser import HTMLParser

class MaerskHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.current_tag = None
        self.current_attrs = {}
        self.in_card = False
        self.card_depth = 0
        self.card_data = []
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')
        
        # Track elements with card/offer in class
        if 'card' in class_name.lower() or 'offer' in class_name.lower() or 'sailing' in class_name.lower() or 'result' in class_name.lower():
            print(f"Tag: <{tag}>, Class: '{class_name}', Attributes: {attrs_dict}")
            
        self.tags.append((tag, attrs_dict))
        self.current_text = []

    def handle_endtag(self, tag):
        if self.tags:
            self.tags.pop()

    def handle_data(self, data):
        data_str = data.strip()
        if data_str:
            # If we see price or dates, print the containing tag context
            if 'USD' in data_str or 'Departure' in data_str or 'Arrival' in data_str or '938' in data_str or '1,494' in data_str:
                context = []
                for t, attrs in self.tags[-4:]: # print last 4 tags in path
                    cls = attrs.get('class', '')
                    context.append(f"{t}.{cls.replace(' ', '.')}" if cls else t)
                print(f"Text: '{data_str}' inside path: {' -> '.join(context)}")

def main():
    html_file = os.path.join(os.path.dirname(__file__), 'breakdown_html_3.html')
    if not os.path.exists(html_file):
        print(f"Error: {html_file} does not exist.")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("=== STARTING PARSE OF SAVED MAERSK HTML ===")
    parser = MaerskHTMLParser()
    parser.feed(html_content)

if __name__ == '__main__':
    main()
