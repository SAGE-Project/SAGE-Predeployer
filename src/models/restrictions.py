class Restriction:
    def __init__(self, data):
        self.type = data["type"]


class Conflicts(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.alpha_comp_id = data["alphaCompId"]
        self.comps_id_list = data["compsIdList"]


class EqualBound(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.comps_id_list = data["compsIdList"]
        self.bound = data["bound"]


class LowerBound(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.comps_id_list = data["compsIdList"]
        self.bound = data["bound"]


class UpperBound(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.comps_id_list = data["compsIdList"]
        self.bound = data["bound"]


class FullDeployment(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.alpha_comp_id = data["alphaCompId"]
        self.comps_id_list = data["compsIdList"]


class OneToOneDependency(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.alpha_comp_id = data["alphaCompId"]
        self.beta_comp_id = data["betaCompId"]


class RequireProvide(Restriction):
    def __init__(self, data):
        super().__init__(data)
        self.alpha_comp_id = data["alphaCompId"]
        self.beta_comp_id = data["betaCompId"]
        self.alpha_comp_id_instances = data["alphaCompIdInstances"]
        self.beta_comp_id_instances = data["betaCompIdInstances"]
