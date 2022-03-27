SingleProbationAppraisalEmployee = {
  props: ["id"],
  data() {
    return {
      currentComponent: "ProbationFullForm",
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
        result = await fetch("/employee/update-my-probation-appraisal", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });
        jsonResponse = await result.json();
        // ODOO Error catchh
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
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
        return false;
      }
      return true;
    },
    async getData() {
      try {
        result = await fetch("/employee/get-my-probation-appraisal", {
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
        if (this.appraisalData.metaInfo.state == "self_assessment") {
          this.change_component("ProbationSelfAssessment");
        } else if (this.appraisalData.metaInfo.state == "final_comments") {
          this.change_component("EProbationFinalComment");
        } else {
          this.change_component("ProbationFullForm");
        }
        this.setAccessInfo();
      }
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
    toggleChat(val) {
      document.querySelector("#invoice_communication").style.display = val;
    },
  },
  provide() {
    return {
      appraisalData: Vue.computed(() => this.appraisalData),
      currentComponent: Vue.computed(() => this.currentComponent),
      changeComponent: this.change_component,
      submitFunction: this.submitForm,
      showFlashMessage: this.showMessage,
      closeFlashMessage: this.closeMessage,
      toggleChat: this.toggleChat,
    };
  },
  mounted() {
    this.getData();
  },
  components: {
    "side-bar": ProbationSideBarComponent,
    ProbationSelfAssessment,
    ProbationFullForm,
    EProbationFinalComment,
    FlashMessage,
    LoadingComponent,
    ProbationBreadCrumb,
    ProbationSubmitForm,
  },
  template: `
        <div style="width:100%; margin-top: -17px" v-if="!dataLoading && dataExists && ['self_assessment'].includes(appraisalData.state)">
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
        <div class="row mb-5 mt-3" :class="{'my-5': !['self_assessment', 'final_comments'].includes(appraisalData.state)}">
            <p class="bg-white p-2" v-if="appraisalData.state == 'self_assessment'">The duration of your probation period is now complete. Before your supervisor could start conducting your appraisal, please provide your feedback on the sections below. Once finished, you can use the 'Validate and Submit' link on the left side of the screen to submit your feedback. Your supervisor will then proceed with their evaluation.</p>
            <p class="bg-white p-2" v-if="appraisalData.state == 'final_comments'">Your probation appraisal has been completed. Kindly review the feedback evaluation provided by your supervisor below. Once reviewed, you may click on 'Sign and Submit' to finalize the process. If you have any issues with the appraisal or you have any queries or issues, you may use the section at the end of the page to communicate with your supervisor by typing your message and then clicking on 'Send'.</p>
            <ProbationBreadCrumb :state="appraisalData.state" v-if="!dataLoading && dataExists"/>

            <div class="col-lg-3 py-5 pl-4 bg-white bd-right-grey" v-if="!dataLoading && dataExists &&  ['self_assessment'].includes(appraisalData.state) && hasAccess">
                <side-bar @change_component="change_component" sideBarType="employees" :access-data="appraisalData.metaInfo"/>
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': !dataExists || !hasAccess || ['self_assessment'].indexOf(appraisalData.state) == -1 }" class="py-2 p-lg-5" style="background: white; min-height: 400px;">
                <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess">
                            {{ hasAccessMessage }}
                        </div>  
                    </transition>
                    <transition name="component-fade" mode="out-in">
                        <component :is="currentComponent"  submit-type='byEmployee'></component>
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
const probation_app = Vue.createApp({});
probation_app.component(
  "single-probation-appraisal-employee",
  SingleProbationAppraisalEmployee
);
probation_app.mount("#vue_my_probation_appraisal_app");
