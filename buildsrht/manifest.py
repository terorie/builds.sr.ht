from enum import Enum
import subprocess
import uuid
import yaml
import re

class TriggerAction(Enum):
    email = 'email'
    webhook = 'webhook'

class TriggerCondition(Enum):
    success = 'success'
    failure = 'failure'
    always = 'always'

class Trigger:
    def __init__(self, yml):
        if not isinstance(yml, dict):
            raise Exception("Expected trigger to be a dict")
        self.action = TriggerAction(yml["action"])
        self.condition = TriggerCondition(yml["condition"])
        self.attrs = {
            key: yml[key] for key in yml.keys()
                if key not in ["action", "condition"]
        }

    def to_dict(self):
        attrs = self.attrs
        attrs.update({
            "action": self.action.value,
            "condition": self.condition.value,
        })
        return attrs

class Task:
    def __init__(self, yml):
        if not isinstance(yml, dict) or len(yml) != 1:
            raise Exception("Expected task to be a string: string")
        for key in yml:
            if not isinstance(key, str) or not isinstance(yml[key], str):
                raise Exception("Expected task to be a string: string")
            self.name = key
            self.script = yml[key].strip()
        if not re.match(r"^[a-z0-9_-]+$", self.name) or len(self.name) > 128:
            raise Exception("Task name '{}' is invalid (must be all lowercase letters, " +
                "numbers, underscores, and dashes, and <=128 characters)".format(self.name))

    def __repr__(self):
        return "<Task {}>".format(self.name)

class Manifest:
    def __init__(self, yml):
        self.yaml = yml
        image = self.yaml.get("image")
        arch = self.yaml.get("arch")
        packages = self.yaml.get("packages")
        repos = self.yaml.get("repositories")
        sources = self.yaml.get("sources")
        env = self.yaml.get("environment")
        secrets = self.yaml.get("secrets")
        if not image:
            raise Exception("Missing image in manifest")
        if not isinstance(image, str):
            raise Exception("Expected imagease to be a string")
        if packages:
            if not isinstance(packages, list) or not all([isinstance(p, str) for p in packages]):
                raise Exception("Expected packages to be a string array")
        if repos:
            if not isinstance(repos, dict):
                raise Exception("Expected repositories to be a dict")
            for repo in repos:
                if not isinstance(repos[repo], str):
                    raise Exception("Expected url for repository {}".format(repo))
        if sources:
            if not isinstance(sources, list) or not all([isinstance(s, str) for s in sources]):
                raise Exception("Expected sources to be a string array")
        if env:
            if not isinstance(env, dict):
                raise Exception("Expected environment to be a dictionary")
        if secrets:
            if not isinstance(secrets, list) or not all([isinstance(s, str) for s in secrets]):
                raise Exception("Expected secrets to be a UUID array")
            # Will throw exception on invalid UUIDs as well
            secrets = list(map(uuid.UUID, secrets))
        self.image = image
        self.arch = arch
        self.packages = packages
        self.repos = repos
        self.sources = sources
        self.environment = env
        self.secrets = secrets
        tasks = self.yaml.get("tasks")
        if not tasks or not isinstance(tasks, list):
            raise Exception("Attempted to create manifest with no tasks")
        self.tasks = [Task(t) for t in tasks]
        for task in self.tasks:
            if len([t for t in self.tasks if t.name == task.name]) != 1:
                raise Exception("Duplicate task '{}'", task.name)
        triggers = self.yaml.get("triggers")
        self.triggers = [Trigger(t) for t in triggers] if triggers else []

    def __repr__(self):
        return "<Manifest {}, {} tasks>".format(self.image, len(self.tasks))
    
    def to_dict(self):
        return {
            "image": self.image,
            "arch": self.arch,
            "packages": self.packages,
            "repositories": self.repos,
            "sources": self.sources,
            "environment": self.environment,
            "secrets": [str(s) for s in self.secrets] if self.secrets else None,
            "tasks": [{ t.name: t.script } for t in self.tasks],
            "triggers": [t.to_dict() for t in self.triggers] if any(self.triggers) else None,
        }

    def to_yaml(self):
        return yaml.dump(self.to_dict())
