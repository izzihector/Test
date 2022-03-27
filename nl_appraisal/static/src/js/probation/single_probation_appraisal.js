SingleProbationAppraisalParent = {
  props: ["id"],
  data() {
    return {
      currentComponent: "MSetProbationObjective",
      dataLoading: true,
      dataExists: false,
      appraisalData: {},
      error: false,
      message: "",
      messageType: "success",
      flash: false,
      hasAccess: true,
      hasAccessMessage: "",
      chatContainer: null,
    };
  },
  methods: {
    async submitForm(data) {
      try {
        result = await fetch(
          "/supervisor/update-employee-probation-appraisals",
          {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
          }
        );
        jsonResponse = await result.json();

        // ODOO Error Catch
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        // Custom Error Catch
        responseData = JSON.parse(jsonResponse.result);
        if (responseData.update_status == "fail") {
          throw new Error(`${responseData.errors}`);
        }
        await this.getData();
        this.showMessage((message = "Saved Successfully!"), (type = "success"));
        if (data.state_returning) {
          location.href = location.href;
        }
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
        return false;
      }
      return true;
    },
    async getData() {
      try {
        result = await fetch("/supervisor/get-employee-probation-appraisals", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ appraisal_id: this.id }),
        });
        jsonResponse = await result.json();
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        this.appraisalData = JSON.parse(jsonResponse.result);
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
      }
      this.dataLoading = false;
      if (Object.keys(this.appraisalData).length > 0) {
        this.dataExists = true;
        if (
          ["objective_setting", "probation_period"].includes(
            this.appraisalData.metaInfo.state
          )
        ) {
          this.change_component("MSetProbationObjective");
        } else if (
          this.appraisalData.metaInfo.state == "supervisor_assessment"
        ) {
          this.change_component("SupervisorAssessment");
        } else if (
          this.appraisalData.metaInfo.state == "done" ||
          this.appraisalData.metaInfo.state == "final_comments" ||
          this.appraisalData.metaInfo.state == "self_assessment"
        ) {
          this.change_component("ProbationFullForm");
        }
        this.setAccessInfo();
      }
    },
    change_component(data) {
      this.currentComponent = data;
      this.setAccessInfo();
      this.toggleChat("block");
    },
    setAccessInfo() {
      this.hasAccess = this.appraisalData.metaInfo.hasCurrentComponentAccess;
      this.hasAccessMessage =
        this.appraisalData.metaInfo.hasCurrentComponentAccessMessage;
    },
    showMessage(message, type) {
      if (type == "error") {
        this.error = true;
      }
      this.message = message;
      this.messageType = type;
      this.flash = true;
    },
    closeMessage() {
      this.flash = false;
      this.message = "";
      this.messageType = "success";
      this.error = false;
    },
    toggleChat(val) {
      document.querySelector("#invoice_communication").style.display = val;
    },
  },
  provide() {
    return {
      appraisalData: Vue.computed(() => this.appraisalData),
      currentComponent: Vue.computed(() => this.currentComponent),
      submitFunction: this.submitForm,
      changeComponent: this.change_component,
      showFlashMessage: this.showMessage,
      closeFlashMessage: this.closeMessage,
      toggleChat: this.toggleChat,
    };
  },
  components: {
    "side-bar": ProbationSideBarComponent,
    MSetProbationObjective,
    SupervisorAssessment,
    ProbationPerformanceFeedback,
    ProbationWayForward,
    FlashMessage,
    LoadingComponent,
    ProbationBreadCrumb,
    ProbationSubmitForm,
    ProbationFullForm,
    ProbationStateReturner,
  },
  mounted() {
    this.getData();
  },
  template: `
        <div style="width:100%; margin-top: -17px" v-if="!dataLoading && dataExists && ['objective_setting', 'supervisor_review', 'performance_period'].includes(appraisalData.state)">
            <div class="row bg-white mt-2">
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size" >Employee Name:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.employee_name }}</div>
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size">Emp. ID No.</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.employee_idc_no }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size">Position Title:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.position }}</div>
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size" >Office/Region:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.office }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size">Manager Name:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.manager_name }}</div>
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size" >Manager Position:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.manager_position }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size" >Review Period:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size"> {{ appraisalData.from_date }} </div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.to_date }}</div>
            </div>
        </div>
        <div class="row mb-5 mt-2" :class="{'my-5': appraisalData.state != 'supervisor_assessment'}">
            <p class="bg-white p-2 page-hint" v-if="appraisalData.state == 'supervisor_assessment'">To start providing your feedback with regards to your subordinate probation appraisal, click on 'Edit'. You can then click on 'Save and Next' to proceed to the next phase of the probation appraisal questionaire. Should you require the employee to provide more feedback or modify their answer before you proceed, you may use the 'Move Back to Self Assessment' button at the end of the page. Use the chatter at the end of the page to communicate with them.</p>
            <ProbationBreadCrumb :state="appraisalData.state" v-if="!dataLoading && dataExists"/>
            <div class="col-lg-3 py-5 pl-4 bg-white position-relative bd-right-grey" v-if="!dataLoading && dataExists && (['objective_setting', 'probation_period', 'supervisor_assessment'].includes(appraisalData.state) && hasAccess) || (currentComponent == 'ProbationStateReturner' && appraisalData.state=='final_comments')">
                <side-bar @change_component="change_component" sideBarType="managers" :access-data="appraisalData.metaInfo"/>            
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': (!dataExists || (!hasAccess || ['objective_setting', 'probation_period', 'supervisor_assessment'].indexOf(appraisalData.state) == -1) && !(currentComponent == 'ProbationStateReturner' && appraisalData.state=='final_comments'))  }" class="py-2 p-lg-5" style="background: white; min-height: 400px;">
            <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess && currentComponent != 'ProbationStateReturner'">
                            {{ hasAccessMessage }}
                        </div>  
                    </transition>
                    <transition name="component-fade" mode="out-in">
                        <component :is="currentComponent" submit-type='byManager'></component>
                    </transition>
                </template>
                <LoadingComponent v-if="dataLoading && !error"/>
                <div v-if="!dataExists && !dataLoading && !error">
                    <h4>No Appraisal Record Found!</h4>
                </div>
            </div>
            <FlashMessage :message='message' v-if="flash" :type='messageType' @close-message='closeMessage' ></FlashMessage>
        </div>
    `,
};
const single_probation_appraisal_app = Vue.createApp({});

single_probation_appraisal_app.component(
  "single-probation-appraisal-parent",
  SingleProbationAppraisalParent
);
single_probation_appraisal_app.mount("#vue_single_probation_appraisal_app");
