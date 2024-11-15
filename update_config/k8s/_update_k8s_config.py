import os,sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CUR_FDIR)


def add_event_ttl(config_lines):
    for i,line in enumerate(config_lines):
        if line.startswith('    - --event-ttl'):
            print('already has event-ttl')
            return
        if line.startswith('    - kube-apiserver'):
            print('inserting event-ttl')
            config_lines.insert(i+1,'    - --event-ttl=72h')
            return
    print("no '    -- kube-apiserver' found")

fpath='/etc/kubernetes/manifests/kube-apiserver.yaml'
with open(fpath) as f:
    content=f.read()
    lines=content.split('\n')
    # add --event-ttl
    add_event_ttl(lines)
    with open(fpath,'w') as f:
        f.write('\n'.join(lines))