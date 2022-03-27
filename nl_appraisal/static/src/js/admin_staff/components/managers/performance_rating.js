MPerformanceRating = {
  inject: ["appraisalData", "submitFunction", "changeComponent", "toggleChat"],
  data() {
    return {
      formData: {},
      disableButton: false,
      buttonText: "Save and next",
      readOnlyMode: true,
      editButtonText: "Edit",
    };
  },
  watch: {
    appraisalData: {
      handler(newVal, oldVal) {
        if (newVal.value) this.writeDataToForm(newVal);
      },
      immediate: true,
      deep: true,
    },
  },
  methods: {
    changeReadOnlyMode(changeData = true) {
      this.readOnlyMode = !this.readOnlyMode;
      if (this.readOnlyMode) {
        this.editButtonText = "Edit";
        this.toggleChat("block");
        if (changeData) this.writeDataToForm(this.appraisalData);
      } else {
        this.editButtonText = "Discard";
        this.toggleChat("none");
      }
    },
    writeDataToForm(data) {
      this.formData["appraisal_id"] = data.value["id"];
      this.formData["has_sup_performance_rating"] = true;
      if (data.value["p7_overall_rating"] != 0) {
        this.formData["p7_overall_rating"] = data.value["p7_overall_rating"];
      } else {
        this.formData["p7_overall_rating"] = "";
      }
      this.formData["p7_overall_rating_not_applicable"] =
        data.value["p7_overall_rating_not_applicable"];
      this.formData["p7_emp_contract_rec"] = data.value["p7_emp_contract_rec"];
    },
    async submitForm() {
      this.disableButton = true;
      this.buttonText = "Saving...";
      result = await this.submitFunction(this.formData);
      if (result) {
        this.changeReadOnlyMode((changeData = false));
        if (
          this.appraisalData.value.metaInfo.setting_performance_rating_state
        ) {
          this.changeComponent("SubmitForm");
        }
      }
      this.disableButton = false;
      this.buttonText = "Save and next";
    },
  },
  template: `
        <div>
        <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">
          Final Rating and Recommendation
        </h4>
        <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="200" height="200" viewBox="0 0 955.95262 639.22428"><rect x="0.30042" y="0.39886" width="703.57562" height="450.60114" fill="#e6e6e6"/><rect x="20.419" y="56.91548" width="663.33851" height="171.77293" fill="#fff"/><rect x="185.4182" y="81.72713" width="140.28123" height="8.05267" fill="#e6e6e6"/><rect x="185.4182" y="111.10108" width="216.62477" height="8.05267" fill="#875a7b"/><rect x="185.4182" y="138.7756" width="176.54439" height="8.05267" fill="#e6e6e6"/><rect x="185.4182" y="166.34557" width="103.06377" height="8.05267" fill="#e6e6e6"/><rect x="185.4182" y="193.9155" width="155.54994" height="8.05267" fill="#e6e6e6"/><rect x="121.4805" y="78.86424" width="17.17729" height="17.17729" fill="#e6e6e6"/><rect x="121.4805" y="106.53877" width="17.17729" height="17.17729" fill="#875a7b"/><rect x="121.4805" y="134.2133" width="17.17729" height="17.17729" fill="#e6e6e6"/><rect x="121.4805" y="161.88783" width="17.17729" height="17.17729" fill="#e6e6e6"/><rect x="121.4805" y="189.56235" width="17.17729" height="17.17729" fill="#e6e6e6"/><rect x="533.73553" y="117.9903" width="57.25763" height="57.25764" fill="#e6e6e6"/><rect x="20.419" y="252.54576" width="663.33851" height="171.77293" fill="#fff"/><rect x="151.06361" y="267.81207" width="17.17729" height="17.17728" fill="#e6e6e6"/><rect x="121.4805" y="267.81207" width="17.17729" height="17.17728" fill="#875a7b"/><path d="M534.74755,435.76326a65.04556,65.04556,0,0,0-105.003-9.69992l-4.18616-3.65793a70.59368,70.59368,0,0,1,113.973,10.52622Z" transform="translate(-122.02369 -130.38786)" fill="#e6e6e6"/><path d="M537.36724,508.18169l-4.6134-3.102a65.07765,65.07765,0,0,0,1.99371-69.31644l4.78387-2.83166a70.63742,70.63742,0,0,1-2.16418,75.25012Z" transform="translate(-122.02369 -130.38786)" fill="#875a7b"/><path d="M426.13766,515.92644a70.58952,70.58952,0,0,1-.57926-93.52106l4.18616,3.65793a65.03087,65.03087,0,0,0,.53366,86.15415Z" transform="translate(-122.02369 -130.38786)" fill="#875a7b"/><path d="M478.73772,539.44023a70.70869,70.70869,0,0,1-52.6-23.51382l4.14056-3.709a65.04339,65.04339,0,0,0,102.47562-7.13779l4.6134,3.102A70.55387,70.55387,0,0,1,478.73772,539.44023Z" transform="translate(-122.02369 -130.38786)" fill="#875a7b"/><rect x="533.73553" y="305.03195" width="57.25763" height="57.25763" fill="#e6e6e6"/><rect x="119.09476" y="342.24939" width="57.25764" height="57.25763" fill="#e6e6e6"/><rect width="703.57562" height="29.89047" fill="#875a7b"/><circle cx="22.21219" cy="15.28159" r="5.53997" fill="#fff"/><circle cx="43.24053" cy="15.28159" r="5.53997" fill="#fff"/><circle cx="64.26886" cy="15.28159" r="5.53997" fill="#fff"/><polygon points="817.168 623.704 831.411 623.704 838.188 568.764 817.165 568.765 817.168 623.704" fill="#ffb8b8"/><path d="M935.5583,749.44184l28.05079-.00113h.00113a17.87713,17.87713,0,0,1,17.87616,17.87587v.5809l-45.92723.00171Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><polygon points="781.694 569.766 792.205 579.379 834.284 543.411 818.771 529.224 781.694 569.766" fill="#ffb8b8"/><path d="M904.17525,694.2705,924.875,713.201l.00084.00077a17.87711,17.87711,0,0,1,1.12667,25.25538l-.392.42866L891.71907,707.891Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><polygon points="839.555 430.772 835.518 511.511 845.611 599.316 815.333 603.353 796.158 492.336 790.102 416.642 839.555 430.772" fill="#2f2e41"/><path d="M1009.01348,531.89159s12.111,79.73029-13.12018,105.97064-59.54541,72.66559-59.54541,72.66559L912.126,680.25048l61.5639-65.60089-12.111-44.40668-49.453-23.21265,8.074-55.50842,72.66559-1.00925Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><circle cx="831.41549" cy="192.09457" r="24.71744" fill="#ffb8b8"/><polygon points="851.917 227.224 855.703 232.96 865.796 261.219 857.722 371.226 810.287 372.236 804.232 246.08 816.917 230.224 851.917 227.224" fill="#ccc"/><path d="M907.07976,379.49569l-8.074-1.00925s-2.01849,1.00925-3.02771,8.07394-13.12018,69.63785-13.12018,69.63785l16.14789,76.70258,18.16638-24.22187L906.07055,466.2907l11.10168-42.38828Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><polygon points="887.999 248.099 894.054 248.099 909.193 329.847 895.064 393.43 880.934 370.217 884.971 344.986 882.953 322.783 875.888 309.662 887.999 248.099" fill="#2f2e41"/><path d="M968.045,322.48242l-4.49409-1.12353s-3.37053-19.09984-11.23522-16.8528-28.088,4.49409-28.088-4.49409,19.09985-16.8528,30.335-15.72928,25.58427,4.85076,29.21152,21.34686c5.81465,26.444-11.997,33.12341-11.997,33.12341l.29641-.96282a14.9957,14.9957,0,0,0-4.02865-15.30775Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><path d="M900.01507,378.48644l32.29583-13.12018,7.56934-5.55084,22.708,100.4198,15.13867-45.416-4.54163-58.03155,41.88361,21.69876-14.12939,68.6286-2.0185,26.24036,6.05548,21.19412s21.19409,15.13867,14.1294,31.28656-15.13867,17.15716-15.13867,17.15716-34.31434-32.2958-36.33277-40.36978-5.0462-22.20337-5.0462-22.20337-17.15717,64.59165-37.342,63.58237-20.18488-22.20337-20.18488-22.20337l5.04621-22.20337,8.074-23.21261-4.037-38.35129Z" transform="translate(-122.02369 -130.38786)" fill="#2f2e41"/><path d="M1076.97631,769.61214h-268a1,1,0,0,1,0-2h268a1,1,0,0,1,0,2Z" transform="translate(-122.02369 -130.38786)" fill="#ccc"/></svg>
        </div>
       
            <div class="py-5">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="row bg-white font-wieght-bold">
                        <div class="col-lg-3 border-grey border py-1 px-2 odoo-table-cell" >
                            <strong>Rating</strong>
                        </div>
                        <div class="col-lg-6 border-grey border py-1 px-2 odoo-table-cell" >
                            <strong>Interpretaion</strong>
                        </div>
                        <div class="col-lg-3 border-grey border py-1 px-2 odoo-table-cell" >
                            <strong>Supervisor final rating </strong>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-9 p-0">
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey text-center border py-1 px-2">4.5 – 5</div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Exceptional/Outstanding</div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey text-center border py-1 px-2">3.5 – 4.4</div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Exceeds Expected Performance</div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey text-center border py-1 px-2">2.5 – 3.4</div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Meets Expected Performance</div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey text-center border py-1 px-2">1.5 – 2.4 </div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Required performance improvement</div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey text-center border py-1 px-2">1 – 1.4 </div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Unsatisfactory/Unacceptable Performance</div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-4 border-grey border text-center py-1 px-2">
                                    Not Applicable
                                    <input class="ml-2" type="checkbox" :disabled="readOnlyMode" v-model="formData.p7_overall_rating_not_applicable" name="p7_overall_rating_not_applicable" id="p7_overall_rating_not_applicable" />
                                </div>
                                <div class="col-lg-8 border-grey border py-1 px-2">Not Applicable or Not Able to Evaluate</div>
                            </div>
                        </div>
                        <div class="col-lg-3 border bg-white border-grey" style="padding: 0px">
                            <template v-if="formData.p7_overall_rating_not_applicable">
                                <div style="height: 100%; display: flex; justify-content: center; align-items: center;">N/A</div>
                            </template>
                            <template v-else="">
                                <div style="height: 100%; display: flex; flex-direction:column; text-align:center; justify-content: center; align-items: center;">
                                    <div>{{ formData.p7_overall_rating }}</div>
                                    <div class="mt-2" style="font-size:12px;">
                                        {{ formData.p7_overall_rating >= 4.5 ? 'Exceptional/Outstanding' : formData.p7_overall_rating >= 3.5 ? 'Exceeds Expected Performance' : formData.p7_overall_rating >= 2.5 ? 'Meets Expected Performance' : formData.p7_overall_rating >= 1.5 ? 'Required Performance Improvement' : formData.p7_overall_rating >= 1 ? 'Unsatisfactory/Unacceptable Performance' : ''  }}
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                    <div class="bg-white border border-grey">
                        <div class="col-lg-12 py-2 font-weight-bold">Recommendation on employee contract with SCA (Cycle the applicable option)</div>
                        <select class="form-control" v-model="formData.p7_emp_contract_rec" name="p7_emp_contract_rec" id="p7_emp_contract_rec" :disabled="readOnlyMode" style="text-align: center;">
                            <option value="" style="color: #b1b1b1">select ...</option>
                            <option value="extension_of_contract">Extension of contract</option>
                            <option value="non_renewal_of_contract">Non-renewal of contract</option>
                            <option value="termination_of_contract">Termination of contract</option>
                            <option value="performance_improvement_plan">Performance Improvement plan (Consult HR for process)</option>
                        </select>
                    </div>
                </form>
            </div>
        </div>       
    `,

  // <input  type="number" min="0" max="5" step=0.000000001 class="form-control" placeholder="Rating if applicable" :disabled="readOnlyMode || formData.p7_overall_rating_not_applicable" v-model="formData.p7_overall_rating" name="p7_overall_rating" id="p7_overall_rating" />
};
