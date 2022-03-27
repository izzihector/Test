SingleAppraisalParent = {
  props: ["id"],
  data() {
    return {
      currentComponent: "MSetObjective",
      dataLoading: true,
      dataExists: false,
      appraisalData: {},
      error: false,
      message: "",
      messageType: "success",
      flash: false,
      hasAccess: true,
      hasAccessMessage: "",
    };
  },
  methods: {
    async submitForm(data) {
      try {
        result = await fetch("/supervisor/update-employee-appraisals", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });
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
        result = await fetch("/supervisor/get-employee-appraisals", {
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
          this.appraisalData.metaInfo.state == "supervisor_review" &&
          ["is_only_manager", "both_user"].includes(
            this.appraisalData.manager_type
          )
        ) {
          this.change_component("MObjectiveFeedback");
        } else if (
          this.appraisalData.metaInfo.state == "objective_setting" &&
          ["is_only_manager", "both_user"].includes(
            this.appraisalData.manager_type
          )
        ) {
          this.change_component("MSetObjective");
        } else if (
          this.appraisalData.metaInfo.state == "2nd_supervisor_review" &&
          ["is_only_second_manager", "both_user"].includes(
            this.appraisalData.manager_type
          )
        ) {
          this.change_component("SecondSupervisor");
        } else if (
          this.appraisalData.metaInfo.state == "performance_period" &&
          ["is_only_manager", "both_user"].includes(
            this.appraisalData.manager_type
          )
        ) {
          this.change_component("MSetObjective");
        } else if (
          ["objective_setting", "performance_period"].indexOf(
            this.appraisalData.metaInfo.state
          ) == -1
        ) {
          this.change_component("FullForm");
        } else {
          this.change_component("FullForm");
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
    "side-bar": SideBarComponent,
    MSetObjective,
    MSetLearningObjective,
    MObjectiveFeedback,
    MObjectiveLearningFeedback,
    MEmployeeAssessment,
    MCareerAspiration,
    MSetObjectiveNextYear,
    MSetLearningObjectiveNextYear,
    MPerformanceRating,
    SecondSupervisor,
    AppraisalStateReturner,
    FlashMessage,
    LoadingComponent,
    BreadCrumb,
    SubmitForm,
    FullForm,
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
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size" >Review Period:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size"> {{ appraisalData.from_date }} </div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.to_date }}</div>
            </div>
        </div>
        <div class="row my-5">
            <BreadCrumb :state="appraisalData.state" v-if="!dataLoading && dataExists" appraisalType="adminStaff"/>
            <div class="col-lg-3 py-5 pl-4 bg-white bd-right-grey" v-if="!dataLoading && dataExists &&  ['objective_setting', 'supervisor_review', 'performance_period'].includes(appraisalData.state) && hasAccess || (currentComponent == 'AppraisalStateReturner' && ['2nd_supervisor_review', 'final_comments'].includes(appraisalData.state))">
                <side-bar @change_component="change_component" sideBarType="managers" :access-data="appraisalData.metaInfo"/>
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': (!dataExists || (!hasAccess || ['objective_setting', 'supervisor_review', 'performance_period'].indexOf(appraisalData.state) == -1) && !(currentComponent == 'AppraisalStateReturner' && ['2nd_supervisor_review', 'final_comments'].includes(appraisalData.state))) }" class="py-2 p-lg-5" style="background: white; min-height: 400px;">
                <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess && currentComponent != 'AppraisalStateReturner'">
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
const single_appraisal_app = Vue.createApp({});

single_appraisal_app.component(
  "single-appraisal-parent",
  SingleAppraisalParent
);
single_appraisal_app.mount("#vue_single_appraisal_app");
