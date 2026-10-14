L=open('../../ladder/w3d/index.html').read().split('\n')
def find(prefix,start=0):
    for i in range(start,len(L)):
        if L[i].startswith(prefix): return i
    raise Exception(prefix)
def rng(a,b): return '\n'.join(L[a:b])
i_head_end=find('const TAN=')+1
i_pm=find('// ------------------------------------------------------------------ shared point material')
i_colors=find('const TEAL=')+1
i_glowtex=find('function glowTex')
i_sprite=find('function sprite')+1
i_noise=find('const NOISE=`'); i_noise_end=find('float fbm')+1
i_wrap=find('// ------------------------------------------------------------------ dense scale-free'); i_cam=find('// ------------------------------------------------------------------ camera path')
i_cr=find('function cr('); i_fke=find('const FK=')
i_comp=find('// ------------------------------------------------------------------ composer'); i_sm=find('const sm=')+1
head=rng(0,i_head_end)
pm=rng(i_pm,i_colors)
glow=rng(i_glowtex,i_sprite).replace('const glows=[];','const glows=[];')
noise=rng(i_noise,i_noise_end)
wrap=rng(i_wrap,i_cam)
cr=rng(i_cr,i_fke)
comp=rng(i_comp,i_sm)
new=open('scene.js').read()
html=head+'\n'+pm+'\n'+glow+'\n'+noise+'\n'+wrap+'\n'+cr+'\n'+comp+'\n'+new+'\n</script></body></html>\n'
open('index.html','w').write(html)
print(len(html))
