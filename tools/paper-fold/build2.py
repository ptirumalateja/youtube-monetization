import sys
parts = sys.argv[1:] or ['scenes2.part.js']
head = open('index.html').read().split("// Paper fold 103")[0]
imports = open('build.py').read().split("imports = '''")[1].split("'''")[0]
html = head + imports + open('helpers.part.js').read() + open('objects.part.js').read() + ''.join(open(p).read() for p in parts) + "\n</script></body></html>\n"
open(parts[-1].replace('.part.js','.html').replace('scenes2','reel2'),'w').write(html)
print('ok')
