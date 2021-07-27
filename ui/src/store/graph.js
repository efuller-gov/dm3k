
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
      dm3kGraph: [], //this is the only thing you need...
},
  getters: {},
  mutations: {
    clearGraph(state){
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
      state.dm3kGraph = [] //this is the only thing you need...
    },
    addResource(state, resourceObj) {
      state.resources.push(resourceObj)
    },
    addResourceInstance(state, resPayload){
      let resName = resPayload['instanceName']
      let resourceInstanceObj = resPayload['newInstance']
      state.dm3kGraph.resourceInstances.filter(x=>x.label==resName)[0].instanceTableData.push(resourceInstanceObj)
    },
    addActivity(state, activityObj) {
      // Add AllocationInstance when first create
      let ai = new AllocationInstance(activityObj['existingResName'], activityObj['actName']);
      let costNameList = state.dm3kGraph.resources.filter(x=>x.value == activityObj['existingResName'])[0].budgetNameList
      state.dm3kGraph.activityInstances.push(new ActivityInstance(activityObj['newActType'], activityObj['actName'], costNameList))
      state.dm3kGraph.allocatedToInstances.push(ai);
    },
    addActivityInstance(state, actPayload){
      let actName = actPayload['instanceName']
      let activityInstanceObj = actPayload['newInstance']
      state.dm3kGraph.activityInstances.filter(x=>x.label==actName)[0].instanceTableData.push(activityInstanceObj)
    },
    addContainsLink(state, containsObj){
      state.dm3kGraph.containsLinks.push(containsObj);
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
      let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      state.dm3kGraph.allocatedToInstances.push(ai);
    },
    addCanBeAllocatedTo(state, allocObj){
      state.dm3kGraph.allocatedToInstances.filter(x=>(x.actName==allocObj['actName'] && x.resName==allocObj['existingResName']))[0].instanceTableData.push(
        { activityInstance: "ALL",
          resourceInstance: "ALL"}
      );
    },
    removeResourceInstance(state, resObj){
      state.dm3kGraph.resourceInstances.filter(x=>x.label==resObj['name'])[0]
    },
    addContainsInstance(state, containsObj){
      state.dm3kGraph.containsInstances.filter(x=>(x.childName==containsObj['childName'] && x.parentName==containsObj['parentName']))[0].instanceTableData.push(
        { childInstance: "ALL",
          parentInstance: "ALL"}
      );
    }
  }
});