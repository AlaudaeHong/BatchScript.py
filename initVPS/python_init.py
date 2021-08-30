#! /usr/local/bin/python3
import os
import shutil
import json
import stat

def configuringLocalSSH(config):
    PathToHOme = config["PathToHome"]
    try:
        print("moving id_rsa to .ssh")
        shutil.move("id_rsa", "{0}/.ssh/id_rsa".format(PathToHOme))

        os.chmod("{0}/.ssh/id_rsa".format(PathToHOme), stat.S_IREAD)

    except OSError as err:
        print("OS: configuringLocalSSH: {0}".format(err))
    except IOError as err:
        print("OS: configuringLocalSSH: {0}".format(err))


def configuringVim(PathToHome, UrlToVimrc):
    print("Configuring VIM")

    os.chdir(PathToHome)

    try:
        os.remove(".vimrc")
    except FileNotFoundError:
        print("File .vimrc not existed")

    os.system("wget {URL}".format(URL=UrlToVimrc))

    try:
        os.mkdir(".vim")
    except FileExistsError:
        print("Directory .vim already existed")

    os.system(
        "git clone https://github.com/VundleVim/Vundle.vim.git {Home}/.vim/bundle/Vundle.vim".format(Home=PathToHome))
    os.system("vim +PluginInstall +qall")

    print("VIM Configured")

    return "* Remember to remove YouCompleteMe Plugin on .vimrc\n"


def vim(config):
    try:
        PathToHOme = config["PathToHome"]
        config_Vim = config["Vim"]

        UrlToVimrc = config_Vim["UrlToVimrc"]

        configuringVim(PathToHOme, UrlToVimrc)
    except KeyError as err:
        print("KeyError: Vim: {0}".format(err))


def github(config):
    try:
        GitHub = config["GitHub"]

        Email = GitHub["email"]
        Name = GitHub["name"]

        os.system("git config --global user.email \"{0}\"".format(Email))
        os.system("git config --global user.name \"{0}\"".format(Name))

    except KeyError as err:
        print("KeyError: GitHub: {0}".format(err))


def Docker(config):
    try:
        PathToHOme = config["PathToHome"]
        Course = config["Course"]
        Docker_Config = Course["Docker_Config"]
        DOCKER_REPO = Docker_Config["DOCKER_REPO"]
        DOCKER_TAG = Docker_Config["DOCKER_TAG"]

        os.chdir(PathToHOme)
        Profile = open(".profile", "a")

        Profile.write("\n# Docker Related Environment\n")
        Profile.write("export DOCKER_REPO=\"{0}\"\n".format(DOCKER_REPO))
        Profile.write("export DOCKER_TAG=\"{0}\"\n".format(DOCKER_TAG))
        Profile.write("export DOCKER_IMAGE=$DOCKER_REPO:$DOCKER_TAG\n")
        Profile.write("\n")
        Profile.close()

        AWS_Docker(config)

    except KeyError as err:
        print("KeyError: Docker: {0}".format(err))
    except OSError as err:
        print("OS: Docker: {0}".format(err))


def AWS_Docker(config):
    print("Set AWS ECR(Elastic Container Resigtry)")
    try:
        PathToHOme = config["PathToHome"]
        Course = config["Course"]
        Docker_Config = Course["Docker_Config"]
        AWS_Region = Course["AWS_Region"]

        DOCKER_REPO = Docker_Config["DOCKER_REPO"]

        # Login ECR
        os.system("$(aws ecr get-login --no-include-email)")
        # Try to create REPO
        os.system(
            "aws ecr create-repository --repository-name {0}".format(DOCKER_REPO))

        os.chdir(PathToHOme)
        Profile = open(".profile", "a")

        Profile.write("\n# AWS Docker Repo Related Environment\n")
        Profile.write("export AWS_REPO_REGISTRY=$(aws ecr describe-repositories --repository-names {0} | jq -r .repositories[0].registryId)\n".format(DOCKER_REPO))
        Profile.write("export AWS_REPO_REGISTRYURL=$AWS_REPO_REGISTRY.dkr.ecr.{0}.amazonaws.com\n".format(AWS_Region))
        Profile.write("\n")

        Profile.close()

    except KeyError as err:
        print("KeyError: AWS_Docker: {0}".format(err))


def AWS(config):
    print("Setting up AWS Credential")
    try:
        PathToHOme = config["PathToHome"]
        Course = config["Course"]

        os.chdir(PathToHOme)

        try:
            os.mkdir(".aws")
        except FileExistsError:
            print("Directory .aws already existed")

        os.chdir(".aws")

        Credentials = open("credentials", "w")
        Config = open("config", "w")

        AWS_Configs = Course["AWS_Config"]

        Config.write(
            "[Default]\n"
            "region={0}\n"
            "output=json\n"
            "\n".format(Course["AWS_Region"])
        )
        for AWS_Config in AWS_Configs:
            Config.write("[profile {UserInClass}]\n"
                         "region={AWS_Region}\n"
                         "output=json\n"
                         "\n".format(UserInClass=AWS_Config["UserInClass"], AWS_Region=Course["AWS_Region"]))

        Credentials.write(
            "[default]\n"
            "aws_access_key_id=None\n"
            "aws_secret_access_key=None\n"
            "\n"
        )

        for AWS_Config in AWS_Configs:
            Credentials.write(
                "[{UserInClass}]\n"
                "aws_access_key_id={AccessKeyID}\n"
                "aws_secret_access_key={SecretAccessKey}\n"
                "\n".format(UserInClass=AWS_Config["UserInClass"],
                            AccessKeyID=AWS_Config["AccessKeyID"],
                            SecretAccessKey=AWS_Config["SecretAccessKey"]))

        Config.close()
        Credentials.close()

    except KeyError as err:
        print("KeyError: AWS: {0}".format(err))
    except OSError as err:
        print("OS: AWS: {0}".format(err))


def ACC_AND_CC(config):
    print("Trying to setup for 18709 Advanced Cloud Computing")
    try:
        Course = config["Course"]
        PathToHOme = config["PathToHome"]

        TPZ_USERNAME = Course["TPZ_USERNAME"]
        TPZ_PASSWORD = Course["TPZ_PASSWORD"]
        AWS_CurrentUser = Course["AWS_CurrentUser"]

        os.chdir(PathToHOme)
        Profile = open(".profile", "a")

        Profile.write("\n# TPZ Related Environment\n")
        Profile.write("export TPZ_USERNAME=\"{0}\"\n".format(TPZ_USERNAME))
        Profile.write("export TPZ_PASSWORD=\"{0}\"\n".format(TPZ_PASSWORD))
        Profile.write("\n")

        # Update environment variable in the runtime, needed later in the program
        Profile.write("\n# AWS Credential\n")
        Profile.write("export AWS_PROFILE={0}\n".format(AWS_CurrentUser))
        os.environ["AWS_PROFILE"] = AWS_CurrentUser

        Profile.write("export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)\n")
        Profile.write("export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)\n")
        Profile.write("\n")

        Profile.close()

        print("Clone Project Repo")
        Project_Repo = Course["Project_Repo"]
        os.system("git clone {0}".format(Project_Repo))

    except KeyError as err:
        print("KeyError: ACC_AND_CC: {0}".format(err))
    except OSError as err:
        print("OS: ACC_AND_CC: {0}".format(err))

def Misc_Config():
    os.system("byobu-enable")

if __name__ == "__main__":
    print("Beginning initializing this instance")

    with open('config_init.json') as f:
        config = json.load(f)

        Misc_Config()

        configuringLocalSSH(config)
        vim(config)
        github(config)
        
        AWS(config)
        ACC_AND_CC(config)
        #Docker(config)

    print("All processes are completed, HOWEVER: ")
    print("* Remember to run terraform init at Repo")
    print("* Running \"source ~/.profile\" before returning to work")
