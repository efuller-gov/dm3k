
import Vue from 'vue';
import Vuex from 'vuex';

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
      costs : {}
},
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
      state.resourceInstances.push(resourceObj)
    },
    addResourceInstance(state, resourceInstanceObj){
      state.resources.push(resourceInstanceObj)
    },
    addActivity(state, activityObj) {
      console.log("--> store addActivity: ")
      state.activities.push(activityObj);
      console.log("activityObj ", activityObj)
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
    }
  },
  actions: {}
});