
import Vue from 'vue';
import Vuex from 'vuex';
import {AllocationInstance} from '../js/dm3kgraph/dataClasses';
import {ActivityInstance} from '../js/dm3kgraph/dataClasses';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : [],
      activities: [],
      allocatedLinks : [],
      containsLinks : [],
      constraints : [],
      resourceInstances : [],
      activityInstances : [],
      containsInstances : [],
      allocatedToInstances : [],
      rewards : {},
      budgets : {},
      costs : {},
      dm3kGraph: [],
},
  getters: {},
  mutations: {
    clearGraph(state){
      console.log("--- CLEAR STORE IN STORE")
      state.resources = []
      state.resources = []
      state.activities = []
      state.allocatedLinks = []
      state.containsLinks = []
      state.constraints = []
      state.resourceInstances = []
      state.activityInstances = []
      state.containsInstances = []
      state.allocatedToInstances = []
      state.rewards = {}
      state.budgets = {}
      state.costs = {}
      state.dm3kGraph = []
    },
    addResource(state, resourceObj) {
      state.resources.push(resourceObj)
    },
    addResourceInstance(state, resPayload){
      let resName = resPayload['instanceName']
      let resourceInstanceObj = resPayload['newInstance']
      state.resourceInstances.filter(x=>x.label==resName)[0].instanceTableData.push(resourceInstanceObj)
    },
    addActivity(state, activityObj) {
      state.activities.push(activityObj);
      // Add AllocationInstance when first create
      let ai = new AllocationInstance(activityObj['existingResName'], activityObj['actName']);
      let costNameList = state.resources.filter(x=>x.resName == activityObj['existingResName'])[0].budgetNameList
      state.activityInstances.push(new ActivityInstance(activityObj['newActType'], activityObj['actName'], costNameList))
      state.allocatedToInstances.push(ai);
    },
    addActivityInstance(state, actPayload){
      let actName = actPayload['instanceName']
      let activityInstanceObj = actPayload['newInstance']
      state.activityInstances.filter(x=>x.label==actName)[0].instanceTableData.push(activityInstanceObj)
    },
    addContainsLink(state, containsObj){
      state.containsLinks.push(containsObj);
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
      let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      state.allocatedToInstances.push(ai);
    },
    addCanBeAllocatedTo(state, allocObj){
      state.allocatedToInstances.filter(x=>(x.actName==allocObj['actName'] && x.resName==allocObj['existingResName']))[0].instanceTableData.push(
        { activityInstance: "ALL",
          resourceInstance: "ALL"}
      );
    },
    removeResourceInstance(state, resObj){
      state.resourceInstances.filter(x=>x.label==resObj['name'])[0]
    }
  },
  actions: {}
});