import boto3 

# a simpler way to fetch/get parameters based on a path
def parm_recurs(parm_path:str, with_decrypt:bool=False) -> list:
    try:
#       if session is None:
        ssm = boto3.client('ssm')
        # else:
        #     aws = boto3.session.Session(profile_name='misprod',region_name='ap-southeast-1')
        #     ssm = aws.client('ssm')            

    except Exception as err:
        print(err)
        print("error on service ssm using specified credentials")    

    else:
        response = ssm.get_parameters_by_path(
            Path=parm_path,
            Recursive=False,
            WithDecryption=with_decrypt
        )

        return response['Parameters']


def parm_crawl(parm_list:list, parm_name:str) -> str:
    retval = None
    for p in parm_list:
        if parm_name in p['Name']:
            retval = p['Value']
            break

    return retval