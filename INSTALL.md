Installation and Testing
========================

Adama can be deployed in a development or production context using the accompanying Ansible playbooks. Here, we will cover standing up a development version:

Prequisites
-----------

* Ansible 2.0.2.0 or better
* A host with Ubuntu 14.0.4 LTS installed
* An account on that host and associated public key
* A public IP address attached to the install host
* Optionally: a DNS entry for your server

Set up hosts and host_vars
--------------------------

* Inside `adama/ansible`, set up a hosts file using `hosts.example` as a template
* Set up the `ansible_ssh_*` variables inside `adama/ansible/host_vars` to reflect the IP, login user, and public SSH needed to log into the host
* Set the server name in the various url and other fields to the resolvable DNS name of your host
* Optional: Set mail credentials, etc for monitor and backup functions

Deploy
------

ansible-playbook -i your.hostfile dev.yml

Test
----

export API=http://129.114.6.164/community/v0.3
export ARAPORT_USERNAME=plants
export TOKEN=1234567890abcdef

*Status*

```curl -H "Authorization: Bearer $TOKEN" -L -X GET $API/status

{
    "api": "Adama v0.3", 
    "hash": "5c98ed927d072da07d5b95881a893cd3ef51e288", 
    "status": "success"
}
```

*Create namespace*

```curl -H "Authorization: Bearer $TOKEN" -X POST $API/namespaces -Fname=validate -Fdescription="Testing"


{
    "result": "http://hostname/community/v0.3/validate", 
    "status": "success"
}
```

*List namespaces*
```curl -sL -H "Authorization: Bearer $TOKEN" -X GET $API/namespaces

{
    "result": [
        {
            "description": "Testing", 
            "name": "validate", 
            "self": "http://hostname/community/v0.3/validate", 
            "url": null, 
            "users": {
                "admin": [
                    "POST", 
                    "PUT", 
                    "DELETE"
                ], 
                "anonymous": [
                    "POST", 
                    "PUT", 
                    "DELETE"
                ]
            }
        }
    ], 
    "status": "success"
}
```

*Register service*

```
curl -L -X POST -H "Authorization: Bearer $TOKEN" -F "git_repository=https://github.com/Arabidopsis-Information-Portal/bar_webservices_demos.git" -F "metadata=expressologsByLocus" -F "git_branch=master" $API/validate/services

{
    "message": "registration started", 
    "result": {
        "list_url": "http://hostname/community/v0.3/validate/expressologs_by_locus_v0.2.0/list", 
        "notification": "", 
        "search_url": "http://hostname/community/v0.3/validate/expressologs_by_locus_v0.2.0/search", 
        "state_url": "http://hostname/community/v0.3/validate/expressologs_by_locus_v0.2.0"
    }, 
    "status": "success"
}

```

*Inspect service*

```
curl -L -X GET  -H "Authorization: Bearer $TOKEN" $API/validate/expressologs_by_locus_v0.2.0

{
    "result": {
        "service": {
            "authors": [
                {
                    "email": "vaughn@tacc.utexas.edu", 
                    "name": "Matt Vaughn", 
                    "sponsor_organization": "Texas Advanced Computing Center", 
                    "sponsor_uri": "http://www.tacc.utexas.edu/"
                }
            ], 
            "code_dir": "/tmp/tmpniTupJ/user_code", 
            "description": "Given a valid AGI locus, return homologous genes that exhibit similar expression patterns in equivalent tissues in other plant species", 
            "endpoints": {
                "/search": {
                    "parameters": [
                        {
                            "default": "At2g26230", 
                            "description": "Arabidopsis gene identifier", 
                            "name": "locus", 
                            "required": true, 
                            "type": "string"
                        }
                    ]
                }
            }, 
            "git_branch": "master", 
            "git_repository": "https://github.com/Arabidopsis-Information-Portal/bar_webservices_demos.git", 
            "icon": "BAR.png", 
            "json_path": "", 
            "language": "python", 
            "main_module": "expressologsByLocus/main.py", 
            "metadata": "expressologsByLocus", 
            "name": "expressologs_by_locus", 
            "namespace": "validate", 
            "notify": "", 
            "registration_timestamp": "2016-06-16 18:57:27.657044", 
            "requirements": [], 
            "self": "http://hostname/community/v0.3/validate/expressologs_by_locus_v0.2.0", 
            "sources": [
                {
                    "description": "Return a JSON data structure consisting of all homologous genes that exhibit similar expression patterns in equivalent tissues in other plant species.", 
                    "language": "en-ca", 
                    "provider_email": "nicholas.provart@utoronto.ca", 
                    "provider_name": "Nicholas Provart", 
                    "sponsor_organization_name": "University of Toronto", 
                    "sponsor_uri": "http://www.utoronto.ca/", 
                    "title": "Expressologs Retrieval", 
                    "uri": "http://bar.utoronto.ca/webservices/get_expressologs.php"
                }
            ], 
            "tags": [
                "expression", 
                "arabidopsis", 
                "comparative genomics"
            ], 
            "timeout": 30, 
            "type": "query", 
            "url": "http://bar.utoronto.ca/webservices/get_expressologs.php", 
            "users": {
                "admin": [
                    "POST", 
                    "PUT", 
                    "DELETE"
                ], 
                "anonymous": [
                    "POST", 
                    "PUT", 
                    "DELETE"
                ]
            }, 
            "validate_request": true, 
            "validate_response": false, 
            "version": "0.2.0", 
            "whitelist": {
                "129.114.97.1": {}, 
                "129.114.97.2": {}, 
                "129.116.84.203": {}, 
                "172.17.42.1": {}, 
                "bar.utoronto.ca": {}
            }, 
            "workers": [
                "19e2c9a94ae8878ad250925db1866ae4a146d7057a6823b255b481efa889d095"
            ]
        }
    }, 
    "status": "success"
}
```

*Exercise a service*

```curl -L -GET -H "Authorization: Bearer $TOKEN" $API/validate/expressologs_by_locus_v0.2.0/search?locus=At2g26230

{"result": [
{"relationships": [{"direction": "undirected", "type": "coexpression", "scores": [{"correlation_coefficient": "0.7094"}]}, {"direction": "undirected", "type": "sequence_similarity", "scores": [{"percentage": "69"}]}], "reference": "TAIR10", "locus": "A...
```

