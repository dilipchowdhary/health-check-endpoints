import subprocess
import re
import yaml
import os

def extract_flags(line):
    display_name = None
    server_port = None
    spring_profiles = None
    prop_path = None

    m1 = re.search(r'-Dnewrelic\.config\.process_host\.display_name=([^\s]+)', line)
    if m1:
        display_name = m1.group(1)
    m2 = re.search(r'--server\.port=([^\s]+)', line)
    if m2:
        server_port = m2.group(1)
    m3 = re.search(r'--spring\.profiles\.active=([^\s]+)', line)
    if m3:
        spring_profiles = m3.group(1)
    m4 = re.search(r'-DPROPPATH=([^\s]+)', line)
    if m4:
        prop_path = m4.group(1)
    return display_name, server_port, spring_profiles, prop_path

def extract_mq_details_for_profiles(yaml_path, profiles):
    if not yaml_path or not os.path.isfile(yaml_path) or not profiles:
        return []
    results = []
    try:
        with open(yaml_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
            for profile in profiles:
                found = False
                for doc in docs:
                    if not doc:
                        continue
                    # Find the profile in this doc
                    doc_profile = None
                    if 'spring' in doc and isinstance(doc['spring'], dict):
                        doc_profile = doc['spring'].get('profiles')
                    elif 'spring.profiles' in doc:
                        doc_profile = doc['spring.profiles']
                    if doc_profile == profile:
                        cpf = doc.get('cpf', {})
                        mq = cpf.get('mq', {})
                        if mq:
                            results.append({
                                'profile': profile,
                                'conn-name': mq.get('conn-name'),
                                'channel': mq.get('channel'),
                                'queue-manager': mq.get('queue-manager'),
                                'queue-list-configs': mq.get('queue-list-configs')
                            })
                            found = True
                            break
                if not found:
                    results.append({'profile': profile, 'error': 'No MQ config found'})
        return results
    except Exception as e:
        return [{'error': f"Error reading YAML: {e}"}]

def main():
    result = subprocess.run(['ps', '-ef'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        if 'java' in line:
            display_name, server_port, spring_profiles, prop_path = extract_flags(line)
            if not spring_profiles:
                continue
            profiles = [p.strip() for p in spring_profiles.split(',')]
            if prop_path and os.path.isdir(prop_path):
                yaml_path = os.path.join(prop_path, 'application.yml')
            else:
                yaml_path = prop_path
            print ("-------------------------------------------")
            print(f"display_name(CMD)={display_name} server.port(CMD)={server_port} spring.profiles.active(CMD)={spring_profiles}")
            mq_details_list = extract_mq_details_for_profiles(yaml_path, profiles)
            for mq_details in mq_details_list:
                if 'error' in mq_details:
                    print(f"Profile={mq_details['profile']}: {mq_details['error']}")
                else:
                    print(f"Profile={mq_details['profile']} "
                          f"conn-name={mq_details['conn-name']} "
                          f"channel={mq_details['channel']} "
                          f"queue-manager={mq_details['queue-manager']} "
                          f"queue-list-configs={mq_details['queue-list-configs']}")

if __name__ == "__main__":
    main()




