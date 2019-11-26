#/bin/bash
print_flags()
{
    #define SD_LOAD_BALANCE         0x0001  /* Do load balancing on this domain. */
    #define SD_BALANCE_NEWIDLE      0x0002  /* Balance when about to become idle */
    #define SD_BALANCE_EXEC         0x0004  /* Balance on exec */
    #define SD_BALANCE_FORK         0x0008  /* Balance on fork, clone */
    #define SD_BALANCE_WAKE         0x0010  /* Balance on wakeup */
    #define SD_WAKE_AFFINE          0x0020  /* Wake task to waking CPU */
    #define SD_SHARE_CPUCAPACITY    0x0080  /* Domain members share cpu power */
    #define SD_SHARE_POWERDOMAIN    0x0100  /* Domain members share power domain */
    #define SD_SHARE_PKG_RESOURCES  0x0200  /* Domain members share cpu pkg resources */
    #define SD_SERIALIZE            0x0400  /* Only a single load balancing instance */
    #define SD_ASYM_PACKING         0x0800  /* Place busy groups earlier in the domain */
    #define SD_PREFER_SIBLING       0x1000  /* Prefer to place tasks in a sibling domain */
    #define SD_OVERLAP              0x2000  /* sched_domains of this level overlap */
    #define SD_NUMA                 0x4000  /* cross-node balancing */
  flags[0x1]="SD_LOAD_BALANCE:          Do load balancing on this domain"
  flags[0x2]="SD_BALANCE_NEWIDLE:       Balance when about to become idle"
  flags[0x4]="SD_BALANCE_EXEC:          Balance on exec"
  flags[0x8]="SD_BALANCE_FORK:          Balance on fork, clone"
  flags[0x10]="SD_BALANCE_WAKE:             Balance on wakeup"
  flags[0x20]="SD_WAKE_AFFINE:           Wake task to waking CPU"
  flags[0x80]="SD_SHARE_CPUCAPACITY:    Domain members share cpu power"
  flags[0x100]="SD_SHARE_POWERDOMAIN:   Domain members share power domain"
  flags[0x200]="SD_SHARE_PKG_RESOURCES: Domain members share cpu pkg resources"
  flags[0x400]="SD_SERIALIZE: Only a single load balancing instance"
  flags[0x800]="SD_ASYM_PACKING: Place busy groups earlier in the domain"
  flags[0x1000]="SD_PREFER_SIBLING: Prefer to place tasks in a sibling domain"
  flags[0x2000]="SD_OVERLAP: sched_domains of this level overlap"
  flags[0x4000]="SD_NUM: cross-node balancing"

  DEC=$1

  echo "SD flag: $DEC";

  for (( mask=1; mask<=0x4000; mask= mask *2 )); do
   if [ "$[$mask & $DEC]" != "0" ]; then
      printf "+%4d: %s\n" $mask "${flags[$mask]}"
   else
       printf "%c%4d: %s\n" "-" $mask "${flags[$mask]}"
   fi
  done
}


#print_domain.sh 4751 527 if you want to disable wake_affinity
#print_domain.sh 4783 559 if you want to enable wake_affinity


if [ "$#" -ne 1 ]; then
    echo "set domaon 0's flag to $1, domain 1's flag to $2"
    for CPU in /proc/sys/kernel/sched_domain/*; do
	echo $1 > ${CPU}/domain0/flags;
	echo $2 > ${CPU}/domain1/flags;
    done
fi

for N in /proc/sys/kernel/sched_domain/cpu0/domain*/flags; do
    #  VAL=$(cat /proc/sys/kernel/sched_domain/cpu0/domain0/flags)
    VAL=$(cat $N);
    echo "current val of $N";
    print_flags $VAL;
    ((nr_domain+=1))
done
