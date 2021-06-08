<template>
  <div class="overlapContainer">
    <ul class="buttonList">
      <li @click="toggleShowBtns">
        <v-btn icon class="tool-btn menu-btn" elevation="0" :ripple="false">
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </li>
      <li v-show="showBtns" @click="_fitWidth">
        <v-tooltip right transition="slide-x-transition" color="black" :open-on-hover="true" :open-delay="600">
          <template v-slot:activator="{ on }">
            <v-btn icon class="tool-btn" elevation="3" :ripple="false">
              <v-icon v-on="on">mdi-focus-field-horizontal</v-icon>
            </v-btn>
          </template>
          <span> {{ focusHorizontalTooltip }}<br/></span>
        </v-tooltip>
      </li>
      <li v-show="showBtns" @click="_fitAll">
        <v-tooltip right transition="slide-x-transition" color="black" :open-on-hover="true" :open-delay="600">
          <template v-slot:activator="{ on }">
            <v-btn icon class="tool-btn" elevation="3" :ripple="false">
              <v-icon v-on="on">mdi-focus-field</v-icon>
            </v-btn>
          </template>
          <span> {{ focusTooltip }}<br/></span>
        </v-tooltip>
      </li>
      <li v-show="showBtns" @click="_resizeGrid">
        <v-tooltip right transition="slide-x-transition" color="black" :open-on-hover="true" :open-delay="600">
          <template v-slot:activator="{ on }">
            <v-btn icon class="tool-btn" elevation="3" :ripple="false">
              <v-icon v-on="on">mdi-arrow-expand-horizontal</v-icon>
            </v-btn>
          </template>
          <span v-for="text in resizeTooltip" :key="text"> {{ text }}<br/></span>
        </v-tooltip>
      </li>
    </ul>
    <div class="textinfo">
      <span v-for="text in textInfo" :key="text"> {{ text }} <br/> </span>
    </div>
    <div id="graphContainer" class="container" @wheel="_zoom">
    </div>
  </div>
</template>

<script>

  import {AttackGraph} from '../../graph/attackGraph';
  import { mapGetters, mapState } from 'vuex';
  import * as _ from 'lodash';
  import { VIEW_SIZE } from '../enums/view-size.enum';
  import { VIEW_TYPE } from '../enums/view-type.enum';

  export default {
    name: 'AttackGraph',
    props: {
      isVisible: Boolean,
      triggerFitWidth: Boolean
    },
    data() {
      return {
        showBtns: false,
        attackGraph: {},
        focusHorizontalTooltip: 'Focus the view so all can be seen horizontally',
        focusTooltip: 'Focus the view so all items can be seen',
        resizeTooltip: ['Change how much space the view takes up',
                        'horizontally based on number of times clicked',
                        'Sizes: [1/3, 1/2, 1]'],
        textInfo: ['Select: Click Cell/Header',
                   'Pan: Mouse Drag',
                   'Zoom: Scroll'],
        sizeMode: VIEW_SIZE.FULL_WIDTH
      };
    },
    computed: {
      ...mapGetters([
        'getVisibleMeasures',
        'getSelectedSearchParams'
      ]),
      ...mapState(['attackTactics', 'attackTechniques'])
    },
    watch: {
      getVisibleMeasures: {
        handler: function(currentMeasures, previousMeasures) {
          const currTechArr = _.uniqBy(_.map(_.flatMap(currentMeasures, 'meta.attackTechniques'), function(technique) {
            return _.toUpper(technique);
          }));
          const prevTechArr = _.uniqBy(_.map(_.flatMap(previousMeasures, 'meta.attackTechniques'), function(technique) {
            return _.toUpper(technique);
          }));
          const techStillSelected = _.intersection(currTechArr, prevTechArr);
          const techNoLongerSelected = _.xor(prevTechArr, techStillSelected);

          if (!_.isEmpty(techNoLongerSelected)) this.clearTechniqueIndicators(techNoLongerSelected);
          this.setTechniquesThatHaveRules(currTechArr);
        },
        deep: true
      },
      getSelectedSearchParams: {
        deep: true,
        handler(updatedSearchParams) {
          const selectedAttackObjArr = _.filter(updatedSearchParams, elem => _.isEqual(VIEW_TYPE.ATTACK, elem.viewType));
          this.setSelectedTechniques(selectedAttackObjArr);
        }
      },
      isVisible: function (val) {
        if (val) {
          this._resetLayout();
        }
      },
      triggerFitWidth: function(val) {
        // no matter the value of the prop just trigger the fit function
        const newContainerHeight = document.getElementById('graphContainer').offsetHeight;
        const newContainerWidth = document.getElementById('graphContainer').offsetWidth;
        this.attackGraph.setGraphMinimumContainerSize(newContainerHeight, newContainerWidth);
        this.attackGraph.fitWidth();
      }
    },
    mounted() {
      this.loadAttackGraph();
      const selectedAttackObjArr = _.filter(this.getSelectedSearchParams, elem => _.isEqual(VIEW_TYPE.ATTACK, elem.viewType));
      this.setSelectedTechniques(selectedAttackObjArr);
    },
    methods: {
      loadAttackGraph() {
        this.attackGraph = new AttackGraph(document.querySelector('#graphContainer'), this.attackTactics, this.attackTechniques);
        this._resetLayout();

        // if boxes selected
        var clickFunction = function(event) {
          for (var box of event.detail.boxesSelected) {
            _.set(box, 'viewType', VIEW_TYPE.ATTACK);
            this.$store.commit('ADD_SELECTED_SEARCH_PARAMS', box);
          }

        }.bind(this);
        document.querySelector('#graphContainer').addEventListener('newBoxesSelected', clickFunction);

        // if boxes UNselected
        var clickFunction2 = function(event) {
          for (var box of event.detail.boxesDeselected) {
            this.$store.commit('REMOVE_SELECTED_SEARCH_PARAMS', box);
          }

        }.bind(this);
        document.querySelector('#graphContainer').addEventListener('newBoxesDeselected', clickFunction2);
      },
      setTechniquesThatHaveRules(techArray) {
        this.attackGraph.setTechniqueIndicators(techArray);
      },
      setSelectedTechniques(techArray) {
        this.attackGraph.setSelectedTechniques(techArray);
      },
      clearTechniqueIndicators(techNoLongerSelected) {
        this.attackGraph.clearTechniqueIndicators(techNoLongerSelected);
      },

      _zoom: function (event) {
        event.preventDefault();
        if (event.deltaY > 0 || event.deltaX > 0) {
          this._zoomOut();
        } else {
          this._zoomIn();
        }
      },

      _zoomIn: function() {
        this.attackGraph.graph.zoomIn();
      },

      _zoomOut: function () {
        this.attackGraph.graph.zoomOut();
      },

      _resetLayout: function () {
        this.attackGraph.fitWidth();
      },

      _fitWidth: function () {
        this.attackGraph.fitWidth();
      },

      _fitAll: function () {
        this.attackGraph.fitAll();
      },

      _resizeGrid: function () {
        this.sizeMode = (this.sizeMode + 1) % 3;
        this.$emit('view-resize', this.sizeMode);
      },

      toggleShowBtns: function () { this.showBtns = !this.showBtns; }
    }
  };

</script>

<style scoped>

  .container {
    border-style: groove;
    border-width: thin;
    border-radius: 5px;
    height: 100%;
    width: 100%;
    padding: 5px;
    max-height: 72vh;
    max-width: 100%;
    overflow: hidden;
    border-color: grey;
    margin: 0px;
    transition: border-color 0.2s ease-in-out;
  }

  .container:hover {
    border-color: #242424;
  }

  #graphContainer {
    width: 100%;
    height: 100%;
    margin: 0px;
    padding: 0px;
    min-height: 72vh;
    overflow: hidden;
  }

  .float-tool-bar {
    position: relative;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    width: 40px;
    height: 200px;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .tool-btn {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #f5f5f5;
    box-shadow: 0 2px 8px 0 #dcdcdc;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    margin-bottom: 5px;
    pointer-events: auto;
  }

  .menu-btn {
    background: transparent;
    transition: 0ms;
  }

  .overlapContainer {
    position: relative;
    width: 100%;
  }

  .buttonList {
    pointer-events: none;
    padding: 5px 0px 0px 5px;
    list-style-type: none;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    z-index: 1
  }

  li {
    pointer-events: none;
  }

  .textinfo {
    position: absolute;
    color: #b3b3b3;
    font-size: 14px;
    padding: 10px;
    bottom: 0px;
  }

</style>
